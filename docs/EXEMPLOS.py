"""
EXEMPLOS DE USO - Virtual Screening Master Refatorado
Demonstra padrões de uso dos novos módulos
"""

# =============================================================================
# EXEMPLO 1: Logging Centralizado
# =============================================================================

from utils import setup_logging, logger

# Configurar logging uma única vez no início da aplicação
setup_logging(
    log_dir="./logs",
    level="DEBUG",
    prefix="meu_app"
)

# Usar logger em qualquer lugar do código
logger.info("Iniciando processo...")
logger.warning("Aviso importante!")
logger.error("Erro crítico!")
logger.debug("Informação para debug")

# Output:
# [2026-01-27 14:30:22] [VirtualScreening] [INFO] Iniciando processo...
# [2026-01-27 14:30:23] [VirtualScreening] [WARNING] Aviso importante!
# [2026-01-27 14:30:24] [VirtualScreening] [ERROR] Erro crítico!
# Logs também salvos em: logs/meu_app_20260127_143022.log


# =============================================================================
# EXEMPLO 2: Validação de Arquivos
# =============================================================================

from utils import file_exists, validate_files_exist, ensure_dir, safe_copy

# Verificar um arquivo
if file_exists("receptor.pdb"):
    logger.info("Arquivo encontrado!")
else:
    logger.warning("Arquivo não encontrado")

# Validar múltiplos arquivos
required_files = ["receptor.pdb", "ligante.sdf", "config.txt"]
if validate_files_exist(required_files, step_name="preparacao"):
    logger.info("Todos os arquivos necessários existem")
else:
    logger.error("Faltam arquivos requeridos")

# Garantir que diretório existe
work_dir = ensure_dir("./screening_results/mapk_Iprodione")
# Cria se não existir, retorna Path object

# Copiar arquivo com tratamento de erro
if safe_copy("source.pdb", "dest.pdb"):
    logger.info("Arquivo copiado com sucesso")
else:
    logger.error("Falha ao copiar arquivo")


# =============================================================================
# EXEMPLO 3: Execução de Subprocesso Robusta
# =============================================================================

from utils import run_subprocess

# Executar comando com timeout e captura de output
result = run_subprocess(
    command=["python3", "preparar_arquivosuniversal.py", "mapk_Iprodione"],
    cwd="./screening_results",
    timeout=600,
    capture_output=True
)

# Verificar resultado
if result.success:
    logger.info("Script executado com sucesso!")
    logger.debug(f"Output: {result.stdout}")
else:
    logger.error(f"Script falhou: {result.error_message}")
    logger.debug(f"Stderr: {result.stderr}")

# Resultado contém:
# - success (bool): Executou sem erro?
# - returncode (int): Código de saída
# - stdout (str): Output padrão
# - stderr (str): Output de erro
# - error_message (str): Mensagem de erro formatada


# =============================================================================
# EXEMPLO 4: Checkpoints (Resume de Pipelines)
# =============================================================================

from utils import Checkpoint, save_checkpoint, load_checkpoint, checkpoint_exists
from datetime import datetime

# Salvar checkpoint após cada passo concluído
checkpoint = Checkpoint(
    last_completed_step="preparacao",
    timestamp=datetime.now().isoformat(),
    target="mapk",
    drug="Iprodione",
    status="running",
    failed_step=None,
    error_message=None
)

checkpoint_file = "./screening_results/mapk_Iprodione/.checkpoint.json"
save_checkpoint(checkpoint_file, checkpoint)
# Arquivo criado: {"last_completed_step": "preparacao", ...}

# Verificar se existe checkpoint
if checkpoint_exists(checkpoint_file):
    logger.info("Checkpoint existe, poderia resumir daqui")
    cp = load_checkpoint(checkpoint_file)
    logger.info(f"Última etapa completa: {cp.last_completed_step}")
    logger.info(f"Status: {cp.status}")


# =============================================================================
# EXEMPLO 5: Interpolação de Variáveis
# =============================================================================

from utils import interpolate_string, interpolate_list

context = {
    "target": "mapk",
    "drug": "Iprodione",
    "year": 2026
}

# Interpolação de string única
template = "{target}_{drug}_resultado_{year}.pdb"
result = interpolate_string(template, context)
# result = "mapk_Iprodione_resultado_2026.pdb"

# Interpolação de lista
templates = [
    "{target}.pdb",
    "ligante_{drug}.sdf",
    "config_{year}.txt"
]
results = interpolate_list(templates, context)
# results = ["mapk.pdb", "ligante_Iprodione.sdf", "config_2026.txt"]


# =============================================================================
# EXEMPLO 6: PipelineStep (Abstração de Passos)
# =============================================================================

from pipeline_step import PipelineStep, StepConfig, PythonScriptStep
from pathlib import Path

# Criar configuração de passo
step_config_dict = {
    "name": "preparacao",
    "description": "Preparação de arquivos PDBQT",
    "script": "preparar_arquivosuniversal.py",
    "required_input_files": ["receptor.pdb", "ligante.sdf"],
    "expected_output_files": ["receptor.pdbqt", "ligante.pdbqt"],
    "skip_if_missing": False
}

context = {"target": "mapk", "drug": "Iprodione"}
work_dir = "./screening_results/mapk_Iprodione"

# Factory cria instância apropriada (automático)
from pipeline_step import create_pipeline_step
step = create_pipeline_step(step_config_dict, work_dir, context)

# Executar (com validação automática)
if step.execute():
    logger.info("✅ Passo executado com sucesso")
    logger.info(f"Tempo de execução: {step.execution_time:.1f}s")
else:
    logger.error("❌ Passo falhou")
    if step.skip_reason:
        logger.info(f"Motivo: {step.skip_reason}")


# =============================================================================
# EXEMPLO 7: Passo Customizado
# =============================================================================

from pipeline_step import PipelineStep, StepConfig
from utils import ProcessResult, run_subprocess

class CustomAnalysisStep(PipelineStep):
    """Passo customizado que não existe na lista padrão"""
    
    def execute_impl(self) -> ProcessResult:
        logger.info("Executando análise customizada...")
        
        # Sua lógica aqui
        result = run_subprocess(
            ["python3", "meu_script_customizado.py", str(self.work_dir)],
            timeout=300
        )
        
        # Log customizado
        if result.success:
            logger.info("Análise customizada concluída!")
        
        return result

# Uso
custom_step = CustomAnalysisStep(
    StepConfig(
        name="custom_analysis",
        description="Minha análise customizada",
        expected_output_files=["custom_result.txt"]
    ),
    work_dir="./screening_results/mapk_Iprodione",
    context={"target": "mapk", "drug": "Iprodione"}
)

if custom_step.execute():
    logger.info("Sucesso!")


# =============================================================================
# EXEMPLO 8: Verificação de Dependências
# =============================================================================

from utils import check_dependencies, check_executable_in_path

# Verificar executáveis requeridos
required_tools = ["vina", "obabel", "plip"]
all_ok, missing = check_dependencies(required_tools)

if all_ok:
    logger.info("✅ Todas as ferramentas estão instaladas")
else:
    logger.error(f"❌ Ferramentas ausentes: {missing}")
    logger.info("Instale com: pip install -r requirements.txt")

# Ou verificar um único executável
if check_executable_in_path("vina"):
    logger.info("Vina está disponível")


# =============================================================================
# EXEMPLO 9: Formatação de Tempo
# =============================================================================

from utils import format_time_elapsed

tempos = [30.5, 120.3, 3600.7, 7200.5]

for t in tempos:
    print(f"{t}s = {format_time_elapsed(t)}")
    # 30.5s = 30.5s
    # 120.3s = 2.0min
    # 3600.7s = 1.0h
    # 7200.5s = 2.0h


# =============================================================================
# EXEMPLO 10: Configuração (YAML)
# =============================================================================

# Arquivo config.yaml:
"""
targets:
  - mapk
  - pdrk

drugs:
  - Iprodione
  - Fludioxonil

paths:
  output_dir: ./screening_results
  log_dir: ./logs

pipeline_steps:
  - name: "preparacao"
    script: "preparar_arquivosuniversal.py"
    required_input_files:
      - "{target}.pdb"
      - "{drug}.sdf"
    expected_output_files:
      - "receptor.pdbqt"
      - "ligante.pdbqt"
"""

# Carregado no main
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

targets = config["targets"]  # ["mapk", "pdrk"]
drugs = config["drugs"]      # ["Iprodione", "Fludioxonil"]
pipeline = config["pipeline_steps"]  # Lista de dicts

for target in targets:
    for drug in drugs:
        logger.info(f"Processando {target} vs {drug}")
        # Executar pipeline aqui...
