"""
Config centralizado de caminhos e configurações do projeto
Carrega targets.json e drugs.json para descoberta automática
"""

import json
import os
from pathlib import Path

# Diretório base do projeto
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Diretórios principais
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
CONFIG_DIR = PROJECT_ROOT / "config"
RESULTS_DIR = PROJECT_ROOT / "results"
DOCS_DIR = PROJECT_ROOT / "docs"
LOGS_DIR = PROJECT_ROOT / "logs"

# Subdiretórios de templates
PROTEINS_DIR = TEMPLATES_DIR / "proteins"
DRUGS_DIR = TEMPLATES_DIR / "drugs"

# Criar diretórios se não existirem
LOGS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Carregar metadados
TARGETS_FILE = CONFIG_DIR / "targets.json"
DRUGS_FILE = CONFIG_DIR / "drugs.json"
YAML_CONFIG = CONFIG_DIR / "config.yaml"

def load_targets_metadata():
    """Carrega metadata de targets.json"""
    if TARGETS_FILE.exists():
        with open(TARGETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('targets', {}), data.get('default_targets', [])
    return {}, []

def load_drugs_metadata():
    """Carrega metadata de drugs.json"""
    if DRUGS_FILE.exists():
        with open(DRUGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('drugs', {}), data.get('default_drugs', [])
    return {}, []

# Carregar ao importar
TARGETS_META, DEFAULT_TARGETS = load_targets_metadata()
DRUGS_META, DEFAULT_DRUGS = load_drugs_metadata()

def get_target_pdb(target_name: str) -> Path:
    """Retorna caminho completo do PDB de um target"""
    if target_name in TARGETS_META:
        pdb_path = TARGETS_META[target_name].get('pdb_file', '')
        # Resolver caminho relativo
        if pdb_path.startswith('../'):
            return CONFIG_DIR / pdb_path
        elif pdb_path.startswith('..'):
            return PROTEINS_DIR / Path(pdb_path).name
        else:
            return PROTEINS_DIR / pdb_path
    return PROTEINS_DIR / f"{target_name}.pdb"

def get_drug_sdf(drug_name: str) -> Path:
    """Retorna caminho completo do SDF de uma drug"""
    if drug_name in DRUGS_META:
        sdf_path = DRUGS_META[drug_name].get('sdf_file', '')
        # Resolver caminho relativo
        if sdf_path.startswith('../'):
            return CONFIG_DIR / sdf_path
        elif sdf_path.startswith('..'):
            return DRUGS_DIR / Path(sdf_path).name
        else:
            return DRUGS_DIR / sdf_path
    return DRUGS_DIR / f"{drug_name}.sdf"

def get_work_dir(target: str, drug: str) -> Path:
    """Retorna caminho do diretório de trabalho para um target-drug"""
    work_dir_name = f"{target.lower()}_{drug.replace(' ', '_')}"
    return RESULTS_DIR / work_dir_name

# Exports úteis
__all__ = [
    'PROJECT_ROOT',
    'SCRIPTS_DIR',
    'TEMPLATES_DIR',
    'CONFIG_DIR',
    'RESULTS_DIR',
    'DOCS_DIR',
    'LOGS_DIR',
    'PROTEINS_DIR',
    'DRUGS_DIR',
    'TARGETS_META',
    'DRUGS_META',
    'DEFAULT_TARGETS',
    'DEFAULT_DRUGS',
    'get_target_pdb',
    'get_drug_sdf',
    'get_work_dir',
]
