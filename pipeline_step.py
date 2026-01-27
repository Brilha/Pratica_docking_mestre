"""
Abstração de Passos do Pipeline Virtual Screening
Define a interface PipelineStep e suas implementações
"""

import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from utils import (
    logger, ProcessResult, run_subprocess, file_exists, 
    validate_files_exist, ensure_dir, interpolate_string, 
    interpolate_list, format_time_elapsed, safe_move
)


@dataclass
class StepConfig:
    """Configuração de um passo do pipeline"""
    name: str
    description: str
    script: Optional[str] = None
    executable: Optional[str] = None
    required_input_files: Optional[List[str]] = None
    expected_output_files: Optional[List[str]] = None
    fallback_on_missing: Optional[str] = None
    skip_if_missing: bool = False
    rename_outputs: Optional[Dict[str, str]] = None
    log_file: Optional[str] = None
    category: Optional[str] = None  # ✅ NOVO: categoria para scripts opcionais


class PipelineStep(ABC):
    """
    Classe base abstrata para um passo do pipeline
    
    Define a interface comum e gerenciamento de contexto para qualquer etapa.
    """
    
    def __init__(self, config: StepConfig, work_dir: str, context: Dict[str, Any]):
        self.config = config
        self.work_dir = Path(work_dir)
        self.context = context  # {target, drug, etc}
        self.result: Optional[ProcessResult] = None
        self.execution_time = 0
        self.skip_reason = None
        
        logger.debug(f"PipelineStep inicializado: {config.name}")
    
    def get_required_files(self) -> List[str]:
        """Interpola lista de arquivos requeridos com contexto"""
        if not self.config.required_input_files:
            return []
        return interpolate_list(self.config.required_input_files, self.context)
    
    def get_expected_output_files(self) -> List[str]:
        """Interpola lista de arquivos esperados com contexto"""
        if not self.config.expected_output_files:
            return []
        return interpolate_list(self.config.expected_output_files, self.context)
    
    def validate_inputs(self) -> bool:
        """Verifica se arquivos de entrada existem"""
        required = self.get_required_files()
        
        if not required:
            return True
        
        full_paths = [str(self.work_dir / f) for f in required]
        missing = [f for f in full_paths if not file_exists(f)]
        
        if missing:
            logger.warning(
                f"[{self.config.name}] Arquivos de entrada ausentes: {missing}"
            )
            
            # Verificar se pode pular
            if self.config.skip_if_missing:
                self.skip_reason = "Arquivos de entrada ausentes"
                return False
            
            return False
        
        return True
    
    def validate_outputs(self) -> bool:
        """Verifica se arquivos de saída foram criados"""
        expected = self.get_expected_output_files()
        
        if not expected:
            logger.debug(f"[{self.config.name}] Nenhuma validação de saída configurada")
            return True
        
        full_paths = [str(self.work_dir / f) for f in expected]
        missing = [f for f in full_paths if not file_exists(f)]
        
        if missing:
            logger.error(
                f"[{self.config.name}] Arquivos de saída não foram criados: {missing}"
            )
            return False
        
        logger.info(f"[{self.config.name}] ✅ Arquivos de saída validados")
        return True
    
    def handle_output_renames(self) -> bool:
        """Renomeia arquivos de saída se configurado"""
        if not self.config.rename_outputs:
            return True
        
        try:
            for old_name, new_name in self.config.rename_outputs.items():
                old_path = self.work_dir / old_name
                new_path = self.work_dir / new_name
                
                if file_exists(str(old_path)):
                    safe_move(str(old_path), str(new_path))
            
            return True
        except Exception as e:
            logger.error(f"[{self.config.name}] Erro ao renomear arquivos: {e}")
            return False
    
    @abstractmethod
    def execute_impl(self) -> ProcessResult:
        """Implementação concreta da execução (subclasses definem)"""
        pass
    
    def execute(self) -> bool:
        """
        Executa passo com validação e tratamento de erro completo
        
        Returns:
            True se sucesso, False caso contrário
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[{self.config.name}] {self.config.description}")
        logger.info(f"{'='*70}")
        
        start_time = time.time()
        
        # Passo 1: Validar inputs
        if not self.validate_inputs():
            if self.skip_reason:
                logger.warning(f"[{self.config.name}] ⏭️  Pulando: {self.skip_reason}")
                return True  # Skip é considerado sucesso
            else:
                logger.error(f"[{self.config.name}] ❌ Inputs inválidos. Abortando.")
                return False
        
        # Passo 2: Executar
        try:
            self.result = self.execute_impl()
            
            if not self.result.success:
                logger.error(f"[{self.config.name}] ❌ Execução falhou")
                return False
            
            logger.info(f"[{self.config.name}] ✅ Execução concluída")
        
        except Exception as e:
            logger.error(f"[{self.config.name}] ❌ Erro durante execução: {e}")
            return False
        
        # Passo 3: Renomear outputs se necessário
        if not self.handle_output_renames():
            logger.error(f"[{self.config.name}] ❌ Erro ao renomear arquivos de saída")
            return False
        
        # Passo 4: Validar outputs
        if not self.validate_outputs():
            logger.error(f"[{self.config.name}] ❌ Validação de saída falhou")
            return False
        
        self.execution_time = time.time() - start_time
        logger.info(f"[{self.config.name}] ⏱️  Tempo: {format_time_elapsed(self.execution_time)}")
        
        return True


class PythonScriptStep(PipelineStep):
    """Passo que executa um script Python"""
    
    def execute_impl(self) -> ProcessResult:
        """Executa script Python passando folder como argumento"""
        if not self.config.script:
            return ProcessResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="Nenhum script configurado",
                error_message="Script não definido na configuração"
            )
        
        # ✅ CORRIGIDO: Buscar script em scripts/ se não estiver em caminho absoluto
        script_name = self.config.script
        
        # Tentar diferentes localizações
        script_path = None
        
        # 1. Tentar como caminho relativo a partir do root
        candidate = Path(script_name)
        if candidate.exists():
            script_path = candidate
        
        # 2. Tentar em scripts/
        if not script_path:
            candidate = Path("scripts") / script_name
            if candidate.exists():
                script_path = candidate
        
        # 3. Tentar em scripts/preparacao/
        if not script_path:
            candidate = Path("scripts/preparacao") / script_name
            if candidate.exists():
                script_path = candidate
        
        # 4. Tentar em scripts/docking/
        if not script_path:
            candidate = Path("scripts/docking") / script_name
            if candidate.exists():
                script_path = candidate
        
        # 5. Tentar em scripts/analise/
        if not script_path:
            candidate = Path("scripts/analise") / script_name
            if candidate.exists():
                script_path = candidate
        
        # 6. Tentar em scripts/relatorio/
        if not script_path:
            candidate = Path("scripts/relatorio") / script_name
            if candidate.exists():
                script_path = candidate
        
        # 7. Tentar em scripts/utils/
        if not script_path:
            candidate = Path("scripts/utils") / script_name
            if candidate.exists():
                script_path = candidate
        
        if not script_path:
            return ProcessResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"Script não encontrado: {script_name}",
                error_message=f"Procurou em: root, scripts/, scripts/*/. Arquivo não existe."
            )
        
        # Usar caminho absoluto do script
        # ✅ NOVO: Passos especiais podem receber argumentos extras
        command = ["python3", str(script_path.absolute()), str(self.work_dir)]
        
        # ✅ NOVO: Para script "analise_quimica_completa.py" passar nome da droga
        if self.config.script == "analise_quimica_completa.py":
            drug_name = self.context.get("drug", "")
            if drug_name:
                command.append(drug_name)
        
        logger.debug(f"Executando: {' '.join(command)}")
        
        # Executar a partir do diretório raiz do projeto
        return run_subprocess(command, cwd=".")


class VinaStep(PipelineStep):
    """Passo especializado para executar AutoDock Vina"""
    
    def execute_impl(self) -> ProcessResult:
        """Executa Vina com configuração e redirecionamento de log"""
        if not self.config.executable:
            return ProcessResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr="Vina executável não configurado",
                error_message="Executável não definido"
            )
        
        command = [
            self.config.executable,
            "--config", "config.txt",
            "--out", "resultado_docking.pdbqt"
        ]
        
        log_file = self.work_dir / (self.config.log_file or "vina.log")
        logger.debug(f"Executando: {' '.join(command)} em {self.work_dir}")
        logger.debug(f"Log será salvo em: {log_file}")
        
        # Executar e capturar output para arquivo de log
        try:
            with open(log_file, 'w') as f_log:
                result = run_subprocess(command, cwd=str(self.work_dir), timeout=600)
                f_log.write(result.stdout)
                if result.stderr:
                    f_log.write("\n[STDERR]\n")
                    f_log.write(result.stderr)
        except Exception as e:
            logger.error(f"Erro ao redirecionar log do Vina: {e}")
        
        return result


class ConditionalStep(PipelineStep):
    """
    Passo que se executa apenas se certas condições forem atendidas
    
    Útil para passos que são opcionais ou dependem de resultados anteriores
    """
    
    def __init__(self, config: StepConfig, work_dir: str, context: Dict[str, Any],
                 condition_func=None):
        super().__init__(config, work_dir, context)
        self.condition_func = condition_func
    
    def should_execute(self) -> bool:
        """Define se passo deve ser executado"""
        if self.condition_func:
            return self.condition_func(self.work_dir)
        return True
    
    def execute_impl(self) -> ProcessResult:
        if not self.should_execute():
            self.skip_reason = "Condição não atendida"
            return ProcessResult(success=True, returncode=0, stdout="", stderr="")
        
        # Delegado para subclasse
        raise NotImplementedError


def create_pipeline_step(step_config: Dict, work_dir: str, context: Dict[str, Any]) -> PipelineStep:
    """
    Factory para criar instância apropriada de PipelineStep baseado em config
    
    Args:
        step_config: Dict com configuração do passo (do YAML)
        work_dir: Diretório de trabalho
        context: Contexto com {target, drug, etc}
    
    Returns:
        Instância apropriada de PipelineStep
    """
    config = StepConfig(**step_config)
    
    # Escolher classe apropriada baseado em config
    if step_config.get("executable") == "vina":
        return VinaStep(config, work_dir, context)
    elif step_config.get("script"):
        return PythonScriptStep(config, work_dir, context)
    else:
        # Default: usar PythonScriptStep
        return PythonScriptStep(config, work_dir, context)
