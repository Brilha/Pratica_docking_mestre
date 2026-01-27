import sys
import os
import numpy as np
from Bio.PDB import PDBParser

def log(mensagem):
    print(f"[GRID-PRO] {mensagem}")

def gerar_grid_universal(pasta_projeto, res_inicio, res_fim):
    # 1. Localiza o PDB na pasta (qualquer um que seja a proteína)
    arquivos = os.listdir(pasta_projeto)
    pdb_file = next((f for f in arquivos if f.endswith(".pdb") and "complexo" not in f and "pose" not in f), None)
    
    if not pdb_file:
        log("❌ Erro: Nenhum arquivo PDB encontrado na pasta.")
        return

    caminho_pdb = os.path.join(pasta_projeto, pdb_file)
    parser = PDBParser(QUIET=True)
    estrutura = parser.get_structure('alvo', caminho_pdb)
    
    coords = []
    # 2. Coleta coordenadas dos resíduos informados
    for modelo in estrutura:
        for cadeia in modelo:
            for residuo in cadeia:
                if int(res_inicio) <= residuo.get_id()[1] <= int(res_fim):
                    for atomo in residuo:
                        coords.append(atomo.get_coord())
    
    if not coords:
        log(f"❌ Erro: Resíduos {res_inicio}-{res_fim} não encontrados no PDB.")
        return

    coords = np.array(coords)
    centro = coords.mean(axis=0)
    # 3. Define tamanho da caixa (ajustado para cobrir o domínio com folga)
    tamanho = coords.max(axis=0) - coords.min(axis=0) + 12.0 

    # 4. Escreve o arquivo de configuração de ALTA PRECISÃO
    output = os.path.join(pasta_projeto, "config_focus.txt")
    with open(output, 'w') as f:
        f.write(f"receptor = receptor.pdbqt\n")
        f.write(f"ligand = ligante.pdbqt\n\n")
        f.write(f"center_x = {centro[0]:.3f}\n")
        f.write(f"center_y = {centro[1]:.3f}\n")
        f.write(f"center_z = {centro[2]:.3f}\n\n")
        f.write(f"size_x = {tamanho[0]:.3f}\n")
        f.write(f"size_y = {tamanho[1]:.3f}\n")
        f.write(f"size_z = {tamanho[2]:.3f}\n\n")
        f.write("exhaustiveness = 32\n") # Esforço computacional elevado
        f.write("spacing = 0.25\n")      # Resolução atômica superior
        f.write("num_modes = 20\n")

    log(f"✅ SUCESSO: 'config_focus.txt' gerado em {pasta_projeto}")
    log(f"📍 Foco: Resíduos {res_inicio} até {res_fim}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python3 refinar_grid_focado.py <PASTA> <RES_INICIO> <RES_FIM>")
    else:
        gerar_grid_universal(sys.argv[1], sys.argv[2], sys.argv[3])