import os
import subprocess
import time
import shutil

# =============================================================================
#  CONFIGURAÇÃO GLOBAL: Alvos e Fármacos
# =============================================================================
# Priorize usar o nome do arquivo local sem o ".pdb" (ex: pdrk)
LISTA_ALVOS = ["mapk"] 

# Use o nome em Inglês para o PubChem (Fludioxonil)
LISTA_DROGAS = ["Iprodione", "Fludioxonil", "pepstatin_3D_minimizado"]

# =============================================================================

def log(mensagem):
    """Exibe mensagens com prefixo no terminal para fácil leitura"""
    print(f"[MESTRE] {mensagem}")

def preparar_pasta_alvo(alvo, droga, nome_pasta):
    """
    LOGICA REFORÇADA: Garante que o PDB local seja usado se o download falhar.
    """
    pdb_local = f"{alvo}.pdb"
    pdb_na_pasta = os.path.join(nome_pasta, f"{alvo}.pdb")

    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)

    # --- PARTE A: PROTEÍNA (ALVO) ---
    if os.path.exists(pdb_local):
        log(f"✅ Sucesso: Usando arquivo local encontrado: {pdb_local}")
        shutil.copy(pdb_local, pdb_na_pasta)
    else:
        log(f"--- Tentando baixar {alvo} online no RCSB PDB ---")
        subprocess.run(["python3", "coleta_dadosuniversal.py"], input=f"{alvo}\n{droga}\n", text=True)

    # --- PARTE B: LIGANTE (DROGA) ---
    sdf_path = os.path.join(nome_pasta, f"{droga}.sdf")
    sdf_raiz = f"{droga}.sdf" # O arquivo que o obabel gerou está aqui

    if os.path.exists(sdf_raiz):
        log(f"✅ Sucesso: Usando ligante local encontrado: {sdf_raiz}")
        shutil.copy(sdf_raiz, sdf_path)
    elif not os.path.exists(sdf_path):
         log(f"--- Arquivo local não encontrado. Forçando download de {droga} ---")
         # Isca de download
         subprocess.run(["python3", "coleta_dadosuniversal.py"], input=f"1hsg\n{droga}\n", text=True, stdout=subprocess.DEVNULL)
         
         pasta_tmp = f"1hsg_{droga.replace(' ', '_')}"
         sdf_tmp = os.path.join(pasta_tmp, f"{droga}.sdf")
         
         if os.path.exists(sdf_tmp):
             shutil.move(sdf_tmp, sdf_path)
             if os.path.exists(pasta_tmp): shutil.rmtree(pasta_tmp)
             log(f"✅ Ligante {droga} obtido via PubChem.")
         else:
             log(f"❌ Erro Crítico: Não foi possível obter o ligante {droga}.")
             return False

    # Retorna True apenas se AMBOS os arquivos essenciais estiverem na pasta
    return os.path.exists(pdb_na_pasta) and os.path.exists(sdf_path)

def rodar_pipeline(alvo, droga):
    """Orquestra a execução de todos os scripts especialistas"""
    alvo_pasta = alvo.lower() 
    print(f"\n{'='*60}\n 🚀 INICIANDO CICLO: {alvo} vs {droga}\n{'='*60}")
    
    nome_pasta = f"{alvo_pasta}_{droga.replace(' ', '_')}"
    
    # PASSO 1: Setup de arquivos
    log("1. Configurando arquivos...")
    if not preparar_pasta_alvo(alvo, droga, nome_pasta):
        log("❌ Falha no setup inicial. Verifique se o PDB local existe.")
        return

    # PASSO 2: Preparação Bioquímica
    log("2. Limpeza e conversão PDBQT...")
    subprocess.run(["python3", "preparar_arquivosuniversal.py", nome_pasta])
    
    # PASSO 3: Definição do GridBox
    log("3. Calculando coordenadas do Sítio Ativo...")
    subprocess.run(["python3", "definir_gridbox.py", nome_pasta])
    
    # Blind Docking Automático: Cobre a proteína toda se não houver ligante nativo
    if not os.path.exists(os.path.join(nome_pasta, "config.txt")):
        log("⚠️ Sítio específico não detectado. Ativando Blind Docking...")
        subprocess.run(["python3", "definir_grid_cego.py", nome_pasta])
        if os.path.exists(os.path.join(nome_pasta, "config_blind.txt")):
            os.rename(os.path.join(nome_pasta, "config_blind.txt"), os.path.join(nome_pasta, "config.txt"))

    # PASSO 4: Simulação de Encaixe (Vina)
    log("4. Executando simulação de Docking (Vina)...")
    cwd_original = os.getcwd()
    os.chdir(nome_pasta)
    try:
        if os.path.exists("config.txt") and os.path.exists("ligante.pdbqt"):
            with open("log_docking.txt", "w") as f_log:
                subprocess.run(["vina", "--config", "config.txt", "--out", "resultado_docking.pdbqt"], stdout=f_log)
            log("✅ Docking finalizado!")
        else:
            log("❌ Erro: Arquivos essenciais para o Vina ausentes.")
    except Exception as e:
        log(f"❌ Erro no Vina: {e}")
    os.chdir(cwd_original)

    # PASSO 5: Filtros de Química Medicinal
    log("5. Avaliando propriedades de fármaco...")
    subprocess.run(["python3", "analise_quimica_completa.py", os.path.join(nome_pasta, f"{droga}.sdf")])

    # PASSO 6: Mapeamento de Interações 3D (PLIP)
    log("6. Mapeando interações atômicas (PLIP)...")
    if os.path.exists(os.path.join(nome_pasta, "resultado_docking.pdbqt")):
        subprocess.run(["python3", "analisar_interacoes.py", nome_pasta])

    # PASSO 7: Geração do Mapa Visual 2D (ProLIF)
    log("7. Gerando diagrama interativo ProLIF...")
    if os.path.exists(os.path.join(nome_pasta, "complexo_final.pdb")):
        subprocess.run(["python3", "interacao_2d_prolif.py", nome_pasta])

    # PASSO 8: Compilação do Dashboard final
    log("8. Gerando Relatório Executivo...")
    subprocess.run(["python3", "gerar_relatorio_final.py", nome_pasta])

if __name__ == "__main__":
    tempo_inicio = time.time()
    for alvo in LISTA_ALVOS:
        for droga in LISTA_DROGAS:
            rodar_pipeline(alvo, droga)
            
    print(f"\n🏁 TRIAGEM FINALIZADA EM {(time.time() - tempo_inicio) / 60:.2f} MINUTOS 🏁")