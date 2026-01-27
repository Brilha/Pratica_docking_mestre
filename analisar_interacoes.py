import sys
import os
import subprocess

def log(mensagem):
    print(f"[PLIP] {mensagem}")

def converter_docking_para_pdb(arquivo_in, arquivo_out):
    """Extrai a melhor pose do docking e converte para PDB usando OpenBabel"""
    log("Convertendo docking para PDB...")
    try:
        # Pega apenas a primeira pose (-f 1 -l 1) para a análise
        subprocess.run(["obabel", "-ipdbqt", arquivo_in, "-opdb", "-O", arquivo_out, "-f", "1", "-l", "1"], check=True)
    except Exception as e:
        log(f"Erro na conversão OBabel: {e}")

def criar_complexo(receptor, ligante, saida):
    """Une a proteína e o ligante em um único arquivo PDB"""
    log("Criando complexo Proteína-Ligante...")
    with open(saida, 'w') as f_out:
        # Lê a proteína e ignora a linha 'END' para não fechar o arquivo antes do tempo
        with open(receptor, 'r') as f_rec:
            for line in f_rec:
                if not line.startswith("END"):
                    f_out.write(line)
        # Lê o ligante e anexa ao final
        with open(ligante, 'r') as f_lig:
            for line in f_lig:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    f_out.write(line)
        f_out.write("END\n")

def rodar_plip(complexo, pasta_destino):
    """Executa o motor do PLIP para mapear as interações e gerar o .pse"""
    log("Rodando motor PLIP (Aguarde)...")
    try:
        # Executa o PLIP gerando o relatório de texto e a sessão do PyMOL (.pse)
        subprocess.run(["plip", "-f", complexo, "-o", pasta_destino, "-y", "-t"], check=True)
        log("✅ Interações mapeadas com sucesso!")
    except Exception as e:
        log(f"Erro ao executar PLIP: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 analisar_interacoes.py <pasta_projeto>")
        sys.exit()
        
    pasta = sys.argv[1]
    arquivos = os.listdir(pasta)
    
    # Identifica os arquivos na pasta pdrk_Fludioxonil
    docking_pdbqt = next((os.path.join(pasta, f) for f in arquivos if "resultado_docking.pdbqt" in f), None)
    receptor_pdb = next((os.path.join(pasta, f) for f in arquivos if f.endswith(".pdb") and "complexo" not in f and "pose" not in f), None)

    if receptor_pdb and docking_pdbqt:
        log(f"✅ Analisando: {os.path.basename(receptor_pdb)} + {os.path.basename(docking_pdbqt)}")
        ligante_pdb = os.path.join(pasta, "melhor_pose.pdb")
        complexo_final = os.path.join(pasta, "complexo_final.pdb")
        
        # Sequência lógica de execução
        converter_docking_para_pdb(docking_pdbqt, ligante_pdb)
        criar_complexo(receptor_pdb, ligante_pdb, complexo_final)
        rodar_plip(complexo_final, pasta)
    else:
        print(f"❌ Erro: Arquivos (pdb/pdbqt) não encontrados na pasta {pasta}")