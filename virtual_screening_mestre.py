"""
Virtual Screening Master Orchestrator - REFATORIZADO v2
Orquestra pipeline completo de docking molecular com Vina
✅ PRIORIZA ARQUIVOS LOCAIS EM templates/ ANTES DE DOWNLOADS
"""

import os
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

# Importar utilidades
from utils import (
    setup_logging, logger, ensure_dir, check_dependencies,
    safe_copy, file_exists, Checkpoint, save_checkpoint, 
    load_checkpoint, format_time_elapsed
)
from pipeline_step import create_pipeline_step

# =============================================================================
# PRIORIZAÇÃO DE ARQUIVOS: TEMPLATES
# =============================================================================

def find_pdb_file(alvo: str) -> Optional[Path]:
    """
    ✅ NOVO: Busca PDB localmente em templates/ ANTES de baixar
    Ordem de prioridade:
    1. templates/proteins/{alvo}.pdb
    2. templates/proteins/{alvo.lower()}.pdb
    3. Retorna None (para tentar download depois)
    """
    templates_proteins = Path("templates/proteins")
    
    # Tentar com case original
    pdb_path = templates_proteins / f"{alvo}.pdb"
    if pdb_path.exists():
        logger.info(f"✅ Encontrado em templates/proteins: {alvo}.pdb")
        return pdb_path
    
    # Tentar com lowercase
    alvo_lower = alvo.lower()
    pdb_path = templates_proteins / f"{alvo_lower}.pdb"
    if pdb_path.exists():
        logger.info(f"✅ Encontrado em templates/proteins: {alvo_lower}.pdb")
        return pdb_path
    
    # Tentar na raiz (fallback para compatibilidade)
    pdb_path = Path(f"{alvo}.pdb")
    if pdb_path.exists():
        logger.info(f"✅ Encontrado na raiz: {alvo}.pdb")
        return pdb_path
    
    logger.debug(f"⚠️  PDB não encontrado localmente para {alvo}")
    return None


def find_sdf_file(droga: str) -> Optional[Path]:
    """
    ✅ NOVO: Busca SDF localmente em templates/drugs/ ANTES de baixar
    Ordem de prioridade:
    1. templates/drugs/{droga}.sdf
    2. templates/drugs/{droga.replace(' ', '_')}.sdf
    3. Retorna None (para tentar download depois)
    """
    templates_drugs = Path("templates/drugs")
    
    # Tentar com nome original (com espaço, se houver)
    sdf_path = templates_drugs / f"{droga}.sdf"
    if sdf_path.exists():
        logger.info(f"✅ Encontrado em templates/drugs: {droga}.sdf")
        return sdf_path
    
    # Tentar com underscore (se há espaço)
    droga_safe = droga.replace(" ", "_")
    sdf_path = templates_drugs / f"{droga_safe}.sdf"
    if sdf_path.exists():
        logger.info(f"✅ Encontrado em templates/drugs: {droga_safe}.sdf")
        return sdf_path
    
    # Tentar na raiz (fallback para compatibilidade)
    sdf_path = Path(f"{droga}.sdf")
    if sdf_path.exists():
        logger.info(f"✅ Encontrado na raiz: {droga}.sdf")
        return sdf_path
    
    logger.debug(f"⚠️  SDF não encontrado localmente para {droga}")
    return None


def mostrar_opcoes_targets_drugs(targets: List[str], drugs: List[str]) -> tuple:
    """
    ✅ NOVO: Menu interativo para escolher quais targets e drugs executar
    
    Permite ao usuário:
    - Escolher targets específicos (ex: 1,2 ou todos ou nenhum)
    - Escolher drugs específicas (ex: 1,3 ou todas ou nenhuma)
    
    Returns:
        Tuple (targets_selecionados, drugs_selecionadas)
    """
    print("\n" + "="*70)
    print("🎯 SELEÇÃO DE ALVOS E FÁRMACOS")
    print("="*70)
    
    # --- PARTE 1: TARGETS ---
    print("\n📋 ALVOS PROTEICOS DISPONÍVEIS:")
    for i, target in enumerate(targets, 1):
        print(f"  {i}. {target}")
    
    print("\n✏️  Digite qual(is) alvo(s) deseja analisar:")
    print("   Opções: números separados por vírgula (ex: 1,2) ou 'todos' ou 'nenhum'")
    escolha_targets = input("→ ").strip().lower()
    
    targets_selecionados = []
    if escolha_targets == "todos":
        targets_selecionados = targets
        logger.info(f"✅ {len(targets)} alvo(s) SELECIONADO(S): {targets}")
    elif escolha_targets == "nenhum" or not escolha_targets:
        logger.info("⚠️  Nenhum alvo selecionado")
    else:
        try:
            indices = [int(x.strip())-1 for x in escolha_targets.split(",")]
            targets_selecionados = [targets[idx] for idx in indices if 0 <= idx < len(targets)]
            if targets_selecionados:
                logger.info(f"✅ {len(targets_selecionados)} alvo(s) SELECIONADO(S): {targets_selecionados}")
            else:
                logger.warning("⚠️  Nenhuma seleção válida de alvos")
        except (ValueError, IndexError):
            logger.warning("⚠️  Entrada inválida. Nenhum alvo selecionado")
    
    if not targets_selecionados:
        logger.warning("⚠️  Nenhum alvo foi selecionado. Abortando.")
        return [], []
    
    # --- PARTE 2: DRUGS ---
    print("\n💊 FÁRMACOS DISPONÍVEIS:")
    for i, drug in enumerate(drugs, 1):
        print(f"  {i}. {drug}")
    
    print("\n✏️  Digite qual(is) fármaco(s) deseja testar:")
    print("   Opções: números separados por vírgula (ex: 1,3) ou 'todos' ou 'nenhum'")
    escolha_drugs = input("→ ").strip().lower()
    
    drugs_selecionadas = []
    if escolha_drugs == "todos":
        drugs_selecionadas = drugs
        logger.info(f"✅ {len(drugs)} fármaco(s) SELECIONADO(S): {drugs}")
    elif escolha_drugs == "nenhum" or not escolha_drugs:
        logger.info("⚠️  Nenhum fármaco selecionado")
    else:
        try:
            indices = [int(x.strip())-1 for x in escolha_drugs.split(",")]
            drugs_selecionadas = [drugs[idx] for idx in indices if 0 <= idx < len(drugs)]
            if drugs_selecionadas:
                logger.info(f"✅ {len(drugs_selecionadas)} fármaco(s) SELECIONADO(S): {drugs_selecionadas}")
            else:
                logger.warning("⚠️  Nenhuma seleção válida de fármacos")
        except (ValueError, IndexError):
            logger.warning("⚠️  Entrada inválida. Nenhum fármaco selecionado")
    
    if not drugs_selecionadas:
        logger.warning("⚠️  Nenhum fármaco foi selecionado. Abortando.")
        return targets_selecionados, []
    
    print("\n" + "="*70)
    total_combinacoes = len(targets_selecionados) * len(drugs_selecionadas)
    logger.info(f"📊 Total de combinações a executar: {total_combinacoes}")
    print("="*70)
    
    return targets_selecionados, drugs_selecionadas


def descobrir_proteinas_humanas() -> List[str]:
    """
    ✅ NOVO: Descobre proteínas humanas em templates/proteinas_humanas/
    Prioriza arquivos locais
    """
    proteinas_humanas = []
    templates_humanas = Path("templates/proteinas_humanas")
    
    if templates_humanas.exists():
        for arquivo in templates_humanas.glob("*.pdb"):
            proteinas_humanas.append(arquivo.stem)
    
    return proteinas_humanas


def mostrar_opcoes_seletividade() -> Optional[str]:
    """
    ✅ NOVO: Menu para ativar seletividade e escolher proteína humana
    
    Returns:
        Nome da proteína humana selecionada ou None
    """
    print("\n" + "="*70)
    print("🧬 ANÁLISE DE SELETIVIDADE (TOXICIDADE)")
    print("="*70)
    
    print("\n⚠️  A seletividade é crítica para evitar toxicidade.")
    print("   Este módulo compara sua proteína alvo com a humana.")
    print("   Se forem idênticas, a droga será tóxica.\n")
    
    proteinas_humanas = descobrir_proteinas_humanas()
    
    if not proteinas_humanas:
        print("⚠️  Nenhuma proteína humana encontrada em templates/proteinas_humanas/")
        print("   Seletividade desativada.\n")
        return None
    
    print("🧬 PROTEÍNAS HUMANAS DISPONÍVEIS:")
    for i, prot in enumerate(proteinas_humanas, 1):
        print(f"  {i}. {prot}")
    
    print("\n✏️  Deseja ativar análise de seletividade?")
    print("   Digite número da proteína humana para comparar, ou 'não' para desativar:")
    escolha = input("→ ").strip().lower()
    
    if escolha == "não" or not escolha:
        logger.info("✅ Análise de seletividade DESATIVADA")
        return None
    
    try:
        idx = int(escolha) - 1
        if 0 <= idx < len(proteinas_humanas):
            prot_selecionada = proteinas_humanas[idx]
            logger.info(f"✅ Seletividade ATIVADA com proteína: {prot_selecionada}")
            return prot_selecionada
        else:
            logger.warning("⚠️  Seleção inválida. Seletividade desativada.")
            return None
    except ValueError:
        logger.warning("⚠️  Entrada inválida. Seletividade desativada.")
        return None


# =============================================================================

def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    """Carrega configuração do arquivo YAML"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"✅ Configuração carregada: {config_file}")
        return config
    except FileNotFoundError:
        logger.error(f"❌ Arquivo de configuração não encontrado: {config_file}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"❌ Erro ao parsear YAML: {e}")
        raise


# =============================================================================
# PREPARAÇÃO DE PASTA COM PRIORIDADE LOCAL
# =============================================================================

def preparar_pasta_alvo(alvo: str, droga: str, config: Dict[str, Any]) -> bool:
    """
    ✅ REFATORIZADO: Prioriza arquivos locais em templates/
    
    Estratégia:
    1. Buscar {alvo}.pdb em templates/proteins/
    2. Se não encontrar, não tenta download (retorna erro)
    3. Buscar {droga}.sdf em templates/drugs/
    4. Se não encontrar, não tenta download (retorna erro)
    
    Isso garante que o sistema SEMPRE usa dados locais quando disponíveis
    """
    from utils import safe_copy
    
    alvo_lower = alvo.lower()
    nome_pasta = f"{alvo_lower}_{droga.replace(' ', '_')}"
    output_dir = Path(config.get("paths", {}).get("output_dir", "./results"))
    work_dir = output_dir / nome_pasta
    
    ensure_dir(str(work_dir))
    
    logger.info(f"Preparando pasta para: {alvo} vs {droga}")
    logger.debug(f"Diretório de trabalho: {work_dir}")
    
    # --- PARTE A: PROTEÍNA (ALVO) ---
    logger.info(f"🔍 Buscando proteína {alvo}...")
    pdb_source = find_pdb_file(alvo)
    
    if pdb_source is None:
        logger.error(f"❌ PDB não encontrado: {alvo}.pdb não existe em templates/proteins/ nem na raiz")
        logger.error(f"   → Coloque o arquivo em templates/proteins/{alvo}.pdb")
        return False
    
    pdb_dest = work_dir / f"{alvo}.pdb"
    if not safe_copy(str(pdb_source), str(pdb_dest)):
        logger.error(f"❌ Falha ao copiar PDB de {pdb_source} para {pdb_dest}")
        return False
    
    logger.info(f"✅ Proteína copiada: {pdb_source} → {pdb_dest}")
    
    # --- PARTE B: LIGANTE (DROGA) ---
    logger.info(f"🔍 Buscando ligante {droga}...")
    sdf_source = find_sdf_file(droga)
    
    if sdf_source is None:
        logger.error(f"❌ SDF não encontrado: {droga}.sdf não existe em templates/drugs/ nem na raiz")
        logger.error(f"   → Coloque o arquivo em templates/drugs/{droga}.sdf")
        return False
    
    sdf_dest = work_dir / f"{droga}.sdf"
    if not safe_copy(str(sdf_source), str(sdf_dest)):
        logger.error(f"❌ Falha ao copiar SDF de {sdf_source} para {sdf_dest}")
        return False
    
    logger.info(f"✅ Ligante copiado: {sdf_source} → {sdf_dest}")
    
    # --- VALIDAÇÃO FINAL ---
    if not (pdb_dest.exists() and sdf_dest.exists()):
        logger.error(f"❌ Arquivos essenciais ausentes para {alvo}/{droga}")
        return False
    
    logger.info(f"✅ Pasta preparada com sucesso: {work_dir}")
    return True

# =============================================================================
# SCRIPTS OPCIONAIS - INTERATIVIDADE COM USUÁRIO
# =============================================================================

def mostrar_opcoes_opcionais(config: Dict[str, Any]) -> Dict[str, bool]:
    """
    ✅ NOVO: Pergunta ao usuário quais scripts opcionais ativar
    
    Returns:
        Dict com {script_name: True/False} para scripts selecionados
    """
    optional_steps = config.get("optional_steps", [])
    
    if not optional_steps:
        logger.info("ℹ️  Nenhum script opcional disponível")
        return {}
    
    logger.info("\n" + "="*70)
    logger.info("📋 SCRIPTS OPCIONAIS DISPONÍVEIS")
    logger.info("="*70)
    
    # Agrupar por categoria
    categorias = {}
    for i, step in enumerate(optional_steps, 1):
        cat = step.get("category", "other")
        if cat not in categorias:
            categorias[cat] = []
        
        print(f"\n{i}. [{cat.upper()}] {step['name']}")
        print(f"   {step['description']}")
        categorias[cat].append((i, step['name']))
    
    print("\n" + "-"*70)
    escolha = input("\n✏️  Quais passos opcionais deseja ativar? (ex: 1,2,3 ou 'todos' ou 'nenhum'): ").strip().lower()
    
    ativados = {}
    
    if escolha == "todos":
        for step in optional_steps:
            ativados[step['name']] = True
        logger.info("✅ Todos os scripts opcionais ATIVADOS")
    elif escolha == "nenhum" or not escolha:
        logger.info("✅ Scripts opcionais DESATIVADOS")
    else:
        try:
            indices = [int(x.strip())-1 for x in escolha.split(",")]
            for idx in indices:
                if 0 <= idx < len(optional_steps):
                    ativados[optional_steps[idx]['name']] = True
            
            if ativados:
                logger.info(f"✅ {len(ativados)} script(s) opcional(is) ATIVADO(S): {list(ativados.keys())}")
            else:
                logger.warning("⚠️  Nenhuma seleção válida. Scripts opcionais desativados.")
        except ValueError:
            logger.warning("⚠️  Entrada inválida. Scripts opcionais desativados.")
    
    return ativados


def rodar_pipeline(alvo: str, droga: str, config: Dict[str, Any], optional_steps: Dict[str, bool] = None, human_protein: Optional[str] = None) -> bool:
    """
    Orquestra a execução de todos os scripts especialistas
    
    Args:
        alvo: Nome do alvo proteico (target)
        droga: Nome do fármaco (drug)
        config: Dicionário de configuração carregado
        optional_steps: Dict com scripts opcionais selecionados
        human_protein: ✅ NOVO: Nome da proteína humana para comparação de seletividade
    
    Returns:
        True se sucesso, False caso contrário
    """
    alvo_lower = alvo.lower()
    nome_pasta = f"{alvo_lower}_{droga.replace(' ', '_')}"
    output_dir = Path(config.get("paths", {}).get("output_dir", "./results"))
    work_dir = output_dir / nome_pasta
    
    print(f"\n{'='*70}")
    print(f"🚀 INICIANDO CICLO: {alvo} vs {droga}")
    print(f"{'='*70}")
    
    # Preparar pasta e arquivos
    logger.info("Passo 1/2: Configurando arquivos...")
    if not preparar_pasta_alvo(alvo, droga, config):
        logger.error("❌ Falha no setup inicial.")
        return False
    
    # Executar pipeline de passos
    logger.info("Passo 2/2: Executando pipeline de análise...")
    
    context = {
        "target": alvo_lower,
        "drug": droga.replace(" ", "_"),
        "alvo": alvo_lower,
        "droga": droga,
        "human_protein": human_protein  # ✅ NOVO: Proteína humana no contexto
    }
    
    # ✅ NOVO: Copiar proteína humana se seletividade foi ativada
    if human_protein:
        human_prot_source = Path("templates/proteinas_humanas") / f"{human_protein}.pdb"
        human_prot_dest = Path(config.get("paths", {}).get("output_dir", "./results")) / nome_pasta / f"human_protein.pdb"
        
        if human_prot_source.exists():
            safe_copy(str(human_prot_source), str(human_prot_dest))
            logger.info(f"🧬 Proteína humana copiada para comparação: {human_protein}")
        else:
            logger.warning(f"⚠️  Proteína humana não encontrada: {human_prot_source}")
            human_protein = None  # Desativar se não encontrar
    
    # Carregar definição dos passos do pipeline
    pipeline_config = config.get("pipeline_steps", [])
    
    if not pipeline_config:
        logger.error("❌ Nenhum passo definido na configuração")
        return False
    
    # ✅ NOVO: Adicionar passos opcionais selecionados
    if optional_steps:
        optional_config = config.get("optional_steps", [])
        for step_config in optional_config:
            if step_config['name'] in optional_steps and optional_steps[step_config['name']]:
                logger.info(f"📌 Adicionando passo opcional ao pipeline: {step_config['name']}")
                pipeline_config.append(step_config)
    
    all_success = True
    relatorio_gerado = False
    
    for step_config in pipeline_config:
        try:
            step = create_pipeline_step(step_config, str(work_dir), context)
            
            if not step.execute():
                logger.error(f"❌ Pipeline falhou no passo: {step_config['name']}")
                all_success = False
                
                # ✅ NOVO: Se falhar no fallback (gridbox), tentar próximo passo (grid_cego é fallback automático)
                # Decidir se deve continuar ou abortar
                if step_config.get("critical", False):
                    logger.error("Este é um passo crítico. Abortando pipeline.")
                    break
            
            # ✅ NOVO: Rastrear se relatório foi gerado (indicador de sucesso efetivo)
            if step_config['name'] == 'relatorio':
                relatorio_gerado = True
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar passo {step_config['name']}: {e}")
            all_success = False
            break
    
    # ✅ NOVO: Considerar sucesso se o relatório foi gerado (mesmo com falhas intermediárias como gridbox)
    if relatorio_gerado:
        logger.info(f"✅ Análise completada com sucesso para {alvo} vs {droga}")
        return True
    
    if all_success:
        logger.info(f"✅ Pipeline completado com sucesso para {alvo} vs {droga}")
    
    return all_success


# =============================================================================
# MAIN
# =============================================================================


if __name__ == "__main__":
    import sys
    
    # Inicializar logging
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    config = load_config(config_file)
    
    # Setup logging
    log_config = config.get("logging", {})
    setup_logging(
        log_dir=config.get("paths", {}).get("log_dir", "./logs"),
        level=log_config.get("level", "INFO"),
        prefix=log_config.get("file_prefix", "screening")
    )
    
    # Verificar dependências
    logger.info("=" * 70)
    logger.info("🔍 VERIFICANDO DEPENDÊNCIAS")
    logger.info("=" * 70)
    
    dependencies = config.get("dependencies", [])
    all_ok, missing = check_dependencies(dependencies)
    
    if not all_ok:
        logger.error(f"❌ Ferramentas ausentes: {missing}")
        logger.error("Instale as dependências e tente novamente.")
        sys.exit(1)
    
    logger.info("✅ Todas as dependências validadas!\n")
    
    # Carregamento de alvos e drogas
    targets = config.get("targets", [])
    drugs = config.get("drugs", [])
    
    if not targets or not drugs:
        logger.error("❌ Nenhum alvo ou droga configurado")
        sys.exit(1)
    
    logger.info(f"📋 Alvos disponíveis: {targets}")
    logger.info(f"💊 Fármacos disponíveis: {drugs}\n")
    
    # ✅ NOVO: Pergunta ao usuário quais targets e drugs executar
    targets_selecionados, drugs_selecionadas = mostrar_opcoes_targets_drugs(targets, drugs)
    
    if not targets_selecionados or not drugs_selecionadas:
        logger.error("❌ Nenhum alvo ou fármaco selecionado. Abortando.")
        sys.exit(1)
    
    # ✅ NOVO: Pergunta sobre análise de seletividade (proteína humana)
    human_protein_selected = mostrar_opcoes_seletividade()
    
    # ✅ NOVO: Pergunta sobre scripts opcionais
    optional_steps = mostrar_opcoes_opcionais(config)
    
    # Executar pipeline
    tempo_inicio = time.time()
    total_sucesso = 0
    total_falha = 0
    
    try:
        for alvo in targets_selecionados:
            for droga in drugs_selecionadas:
                # ✅ NOVO: Passar human_protein junto com optional_steps
                if rodar_pipeline(alvo, droga, config, optional_steps, human_protein_selected):
                    total_sucesso += 1
                else:
                    total_falha += 1
    
    except KeyboardInterrupt:
        logger.warning("⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
    
    finally:
        tempo_total = time.time() - tempo_inicio
        logger.info("\n" + "=" * 70)
        logger.info(f"🏁 TRIAGEM FINALIZADA")
        logger.info("=" * 70)
        logger.info(f"✅ Sucesso: {total_sucesso}")
        logger.info(f"❌ Falhas: {total_falha}")
        logger.info(f"⏱️  Tempo total: {format_time_elapsed(tempo_total)}")
        logger.info("=" * 70)
