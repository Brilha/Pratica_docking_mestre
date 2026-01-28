"""
Módulo de Utilidades para Virtual Screening Pipeline
Centraliza logging, validação, operações com paths e tratamento de erros
"""

import os
import sys
import json
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


# =============================================================================
# LOGGING CENTRALIZADO
# =============================================================================

def setup_logging(log_dir: str = "./logs", level: str = "INFO", prefix: str = "screening") -> logging.Logger:
    """
    Configura logging com saída em arquivo e console
    
    Args:
        log_dir: Diretório para armazenar logs
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        prefix: Prefixo do arquivo de log
    
    Returns:
        Logger configurado
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("VirtualScreening")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Formatar
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler de arquivo
    log_file = Path(log_dir) / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler de console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger global
logger = logging.getLogger("VirtualScreening")


# =============================================================================
# VALIDAÇÃO DE ARQUIVO E CAMINHO
# =============================================================================

def file_exists(filepath: str) -> bool:
    """Verifica se arquivo existe de forma segura"""
    return Path(filepath).exists() and Path(filepath).is_file()


def dir_exists(dirpath: str) -> bool:
    """Verifica se diretório existe"""
    return Path(dirpath).exists() and Path(dirpath).is_dir()


def validate_files_exist(files: List[str], step_name: str = "") -> bool:
    """
    Valida se múltiplos arquivos existem
    
    Args:
        files: Lista de caminhos de arquivo
        step_name: Nome do passo (para mensagens)
    
    Returns:
        True se todos existem, False caso contrário
    """
    missing = [f for f in files if not file_exists(f)]
    
    if missing:
        step_info = f"[{step_name}] " if step_name else ""
        logger.warning(f"{step_info}Arquivos ausentes: {missing}")
        return False
    
    return True


def ensure_dir(dirpath: str) -> Path:
    """Cria diretório se não existir, retorna Path object"""
    path = Path(dirpath)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_copy(src: str, dst: str) -> bool:
    """
    Copia arquivo com tratamento de erro
    
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        if not file_exists(src):
            logger.error(f"Fonte não existe: {src}")
            return False
        
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.debug(f"Copiado: {src} → {dst}")
        return True
    except Exception as e:
        logger.error(f"Erro ao copiar {src} para {dst}: {e}")
        return False


def safe_move(src: str, dst: str) -> bool:
    """Move arquivo com tratamento de erro"""
    try:
        if not file_exists(src):
            logger.error(f"Fonte não existe: {src}")
            return False
        
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dst)
        logger.debug(f"Movido: {src} → {dst}")
        return True
    except Exception as e:
        logger.error(f"Erro ao mover {src} para {dst}: {e}")
        return False


def safe_rmtree(dirpath: str) -> bool:
    """Remove diretório recursivamente com tratamento de erro"""
    try:
        if not dir_exists(dirpath):
            return True  # Já não existe, OK
        
        shutil.rmtree(dirpath)
        logger.debug(f"Diretório removido: {dirpath}")
        return True
    except Exception as e:
        logger.error(f"Erro ao remover {dirpath}: {e}")
        return False


# =============================================================================
# VALIDAÇÃO DE DEPENDÊNCIAS
# =============================================================================

def check_executable_in_path(executable: str) -> bool:
    """Verifica se executável está disponível em PATH"""
    result = subprocess.run(
        ["which", executable],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def check_dependencies(required_tools: List[str]) -> Tuple[bool, List[str]]:
    """
    Valida instalação de todas as ferramentas requeridas
    
    Args:
        required_tools: Lista de executáveis (ex: ["vina", "obabel"])
    
    Returns:
        Tuple: (all_ok, list_of_missing_tools)
    """
    missing = []
    
    for tool in required_tools:
        if not check_executable_in_path(tool):
            missing.append(tool)
            logger.error(f"❌ Ferramenta não encontrada: {tool}")
        else:
            logger.info(f"✅ Ferramenta encontrada: {tool}")
    
    return len(missing) == 0, missing


# =============================================================================
# EXECUÇÃO DE SUBPROCESSO COM TRATAMENTO ROBUSTO
# =============================================================================

@dataclass
class ProcessResult:
    """Resultado da execução de um processo"""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    error_message: Optional[str] = None


def run_subprocess(
    command: List[str],
    cwd: Optional[str] = None,
    timeout: Optional[int] = None,
    capture_output: bool = True
) -> ProcessResult:
    """
    Executa comando em subprocess com tratamento robusto
    
    Args:
        command: Comando e argumentos (ex: ["python3", "script.py", "arg"])
        cwd: Diretório de trabalho
        timeout: Timeout em segundos
        capture_output: Se deve capturar stdout/stderr
    
    Returns:
        ProcessResult com status da execução
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            check=False
        )
        
        success = result.returncode == 0
        
        if not success:
            error_msg = result.stderr or f"Exit code: {result.returncode}"
            logger.error(f"Comando falhou: {' '.join(command)}\nErro: {error_msg}")
        
        return ProcessResult(
            success=success,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            error_message=result.stderr if not success else None
        )
    
    except subprocess.TimeoutExpired:
        error = f"Timeout ({timeout}s) ao executar: {' '.join(command)}"
        logger.error(error)
        return ProcessResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            error_message=error
        )
    
    except Exception as e:
        error = f"Erro ao executar {' '.join(command)}: {str(e)}"
        logger.error(error)
        return ProcessResult(
            success=False,
            returncode=-1,
            stdout="",
            stderr="",
            error_message=error
        )


# =============================================================================
# GERENCIAMENTO DE CHECKPOINTS
# =============================================================================

@dataclass
class Checkpoint:
    """Representa checkpoint de execução"""
    last_completed_step: str
    timestamp: str
    target: str
    drug: str
    status: str  # "running", "completed", "failed"
    failed_step: Optional[str] = None
    error_message: Optional[str] = None


def save_checkpoint(checkpoint_file: str, checkpoint: Checkpoint) -> bool:
    """Salva checkpoint em arquivo JSON"""
    try:
        Path(checkpoint_file).parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_file, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)
        logger.debug(f"Checkpoint salvo: {checkpoint_file}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar checkpoint: {e}")
        return False


def load_checkpoint(checkpoint_file: str) -> Optional[Checkpoint]:
    """Carrega checkpoint de arquivo JSON"""
    try:
        if not file_exists(checkpoint_file):
            return None
        
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            return Checkpoint(**data)
    except Exception as e:
        logger.error(f"Erro ao carregar checkpoint: {e}")
        return None


def checkpoint_exists(checkpoint_file: str) -> bool:
    """Verifica se checkpoint existe"""
    return file_exists(checkpoint_file)


# =============================================================================
# INTERPOLAÇÃO DE VARIÁVEIS
# =============================================================================

def interpolate_string(template: str, context: Dict[str, Any]) -> str:
    """
    Substitui placeholders {var} por valores do contexto
    
    Ex: "{target}_{drug}.sdf" com context={"target": "mapk", "drug": "Iprodione"}
        → "mapk_Iprodione.sdf"
    """
    result = template
    for key, value in context.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def interpolate_list(templates: List[str], context: Dict[str, Any]) -> List[str]:
    """Interpola lista de strings"""
    return [interpolate_string(t, context) for t in templates]


# =============================================================================
# UTILITY
# =============================================================================

def format_time_elapsed(seconds: float) -> str:
    """Formata tempo decorrido em formato legível"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}min"
    else:
        return f"{seconds/3600:.1f}h"
