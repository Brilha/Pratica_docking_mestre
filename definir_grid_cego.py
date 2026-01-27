import sys
import os
import numpy as np

def calcular_grid_cego(pasta_pasta):
    # Procura qualquer arquivo PDB na pasta que não seja o ligante
    arquivos = [f for f in os.listdir(pasta_pasta) if f.endswith(".pdb") and "pose" not in f and "complexo" not in f]
    
    if not arquivos:
        print("Erro: Nenhum PDB adequado encontrado para medir.")
        return

    # Prioriza o receptor limpo se ele existir
    caminho_pdb = os.path.join(pasta_pasta, "receptor_tmp.pdb")
    if not os.path.exists(caminho_pdb):
        caminho_pdb = os.path.join(pasta_pasta, arquivos[0])

    coordenadas = []
    with open(caminho_pdb, 'r') as f:
        for linha in f:
            if linha.startswith(("ATOM", "HETATM")):
                coordenadas.append([float(linha[30:38]), float(linha[38:46]), float(linha[46:54])])

    coords = np.array(coordenadas)
    centro = coords.mean(axis=0)
    # Calcula a extensão da proteína para cobri-la inteira
    dimensoes = coords.max(axis=0) - coords.min(axis=0) + 10.0 # Margem de segurança

    output = os.path.join(pasta_pasta, "config_blind.txt")
    with open(output, 'w') as f:
        f.write(f"receptor = receptor.pdbqt\n")
        f.write(f"ligand = ligante.pdbqt\n\n")
        f.write(f"center_x = {centro[0]:.3f}\n")
        f.write(f"center_y = {centro[1]:.3f}\n")
        f.write(f"center_z = {centro[2]:.3f}\n\n")
        f.write(f"size_x = {dimensoes[0]:.3f}\n")
        f.write(f"size_y = {dimensoes[1]:.3f}\n")
        f.write(f"size_z = {dimensoes[2]:.3f}\n")
        f.write(f"\nexhaustiveness = 8\n")

    print(f"--- Calculando Grid Box para toda a proteína (Blind Docking) ---")
    print(f"   -> Centro Proteína: {centro}")
    print(f"   -> Dimensões Caixa: {dimensoes}")
    print(f"\n>>> SUCESSO: Arquivo 'config_blind.txt' gerado na pasta.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        calcular_grid_cego(sys.argv[1])