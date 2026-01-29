import sys
import os
import subprocess

# Adicionar diretório raiz do projeto ao path para permitir imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.utils.minimize_complex_energy import minimize_complex_structure, detectar_clashes

def log(mensagem):
    print(f"[PLIP] {mensagem}")

def converter_docking_para_pdb(arquivo_in, arquivo_out, extrair_pose=1):
    """
    ✅ NOVO (28/Jan): Extrai pose do docking e converte para PDB usando OpenBabel
    
    Args:
        arquivo_in: arquivo .pdbqt do docking
        arquivo_out: arquivo .pdb de saída
        extrair_pose: Qual pose extrair (1=primeira/blind, -1=melhor/última)
    """
    log("Convertendo docking para PDB...")
    try:
        if extrair_pose == -1:
            # Extrai última pose (melhor affinity) para docking preciso
            log("  → Extraindo MELHOR POSE (última estrutura = melhor affinity)")
            subprocess.run(["obabel", "-ipdbqt", arquivo_in, "-opdb", "-O", arquivo_out, "-l", "1"], check=True)
        else:
            # Extrai primeira pose para docking cego
            log("  → Extraindo PRIMEIRA POSE (blind docking)")
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
    
    # Identifica os arquivos na pasta
    docking_pdbqt = next((os.path.join(pasta, f) for f in arquivos if "resultado_docking.pdbqt" in f), None)
    receptor_pdb = next((os.path.join(pasta, f) for f in arquivos if f.endswith(".pdb") and "complexo" not in f and "pose" not in f), None)

    if receptor_pdb and docking_pdbqt:
        log(f"✅ Analisando: {os.path.basename(receptor_pdb)} + {os.path.basename(docking_pdbqt)}")
        
        # ✅ NOVO (28/Jan): Detectar se docking preciso foi usado
        flag_docking_preciso = os.path.join(pasta, ".docking_preciso")
        if os.path.exists(flag_docking_preciso):
            log("🎯 DOCKING PRECISO DETECTADO - Usando MELHOR POSE")
            extrair_pose = -1  # Última pose = melhor affinity
        else:
            log("🎯 DOCKING CEGO DETECTADO - Usando PRIMEIRA POSE")
            extrair_pose = 1   # Primeira pose = blind
        
        ligante_pdb = os.path.join(pasta, "melhor_pose.pdb")
        complexo_final = os.path.join(pasta, "complexo_final.pdb")
        
        # Sequência lógica de execução
        converter_docking_para_pdb(docking_pdbqt, ligante_pdb, extrair_pose)
        criar_complexo(receptor_pdb, ligante_pdb, complexo_final)
        
        complexo_para_plip = complexo_final
        
        # ✅ NOVO (28/Jan): Minimização APENAS para docking preciso/refinado
        if os.path.exists(flag_docking_preciso):
            log("🔍 Docking preciso: Detectando bad contacts...")
            n_clashes = detectar_clashes(complexo_final)
            log(f"   → {n_clashes} clashes detectados")
            
            THRESHOLD_CLASHES = 100
            if n_clashes > THRESHOLD_CLASHES:
                log(f"⚠️  Muitos clashes ({n_clashes} > {THRESHOLD_CLASHES}), minimizando...")
                success, minimized_pdb = minimize_complex_structure(complexo_final)
                if success:
                    log(f"✅ Complexo minimizado: {os.path.basename(minimized_pdb)}")
                    complexo_para_plip = minimized_pdb
                else:
                    log(f"⚠️  Minimização falhou, usando original")
            else:
                log(f"✅ Estrutura OK ({n_clashes} clashes), pulando minimização")
        else:
            log("✅ Docking cego: Pulando minimização (não necessário)")
        
        rodar_plip(complexo_para_plip, pasta)
    else:
        print(f"❌ Erro: Arquivos (pdb/pdbqt) não encontrados na pasta {pasta}")