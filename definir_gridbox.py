import sys
import os
import numpy as np
from Bio.PDB import PDBParser

def encontrar_centro_ligante(pdb_path):
    print(f"--- Procurando ligante nativo em: {pdb_path} ---")
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('struct', pdb_path)
    
    candidatos = []
    
    # Varre todos os resíduos procurando coisas que não são proteína (HETATM)
    for residue in structure.get_residues():
        # residue.id[0] começa com 'H_' para heteroátomos
        if residue.id[0].startswith('H_'):
            res_nome = residue.get_resname().strip()
            # Ignora águas e íons comuns irrelevantes para centro de massa
            if res_nome not in ['HOH', 'DOD', 'WAT', 'NA', 'CL', 'ZN']:
                candidatos.append(residue)
    
    if not candidatos:
        print(" [AVISO] Nenhum ligante nativo óbvio encontrado.")
        return None

    # Pega o "maior" candidato (com mais átomos) para evitar pegar glicerol ou impurezas
    melhor_ligante = max(candidatos, key=lambda r: len(r))
    print(f"   -> Ligante referência encontrado: {melhor_ligante.get_resname()} (Cadeia {melhor_ligante.get_parent().id})")
    
    # Calcula a média das coordenadas X, Y, Z de todos os átomos
    coords = [atom.get_coord() for atom in melhor_ligante.get_atoms()]
    centro = np.mean(coords, axis=0)
    print(f"   -> Centro calculado: {centro}")
    return centro

def gerar_config_file(pasta, centro):
    caminho_config = os.path.join(pasta, "config.txt")
    
    with open(caminho_config, "w") as f:
        # Arquivos de entrada
        f.write(f"receptor = receptor.pdbqt\n")
        f.write(f"ligand = ligante.pdbqt\n\n")
        
        # Coordenadas (detectadas automaticamente)
        f.write(f"center_x = {centro[0]:.3f}\n")
        f.write(f"center_y = {centro[1]:.3f}\n")
        f.write(f"center_z = {centro[2]:.3f}\n\n")
        
        # Tamanho da caixa (20 Angstroms costuma ser bom para começar)
        f.write(f"size_x = 20\n")
        f.write(f"size_y = 20\n")
        f.write(f"size_z = 20\n\n")
        
        # Parâmetros de simulação
        f.write(f"exhaustiveness = 8\n") # Nível de detalhe (8 é padrão, 32 é publi)
        f.write(f"num_modes = 9\n")      # Quantas poses salvar
        f.write(f"energy_range = 3\n")   # Diferença de energia aceita
        
    print(f"\n>>> SUCESSO: Arquivo de configuração gerado em:\n    {caminho_config}")

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 definir_gridbox.py <pasta_projeto>")
        sys.exit()
        
    pasta = sys.argv[1]
    
    # Procura o PDB original (não o clean)
    arquivos = os.listdir(pasta)
    pdb_original = next((f for f in arquivos if f.endswith(".pdb") and "clean" not in f), None)
    
    if pdb_original:
        caminho_completo = os.path.join(pasta, pdb_original)
        centro = encontrar_centro_ligante(caminho_completo)
        
        if centro is not None:
            gerar_config_file(pasta, centro)
        else:
            print("Não foi possível gerar o config.txt automaticamente (falta de ligante referência).")
    else:
        print("Erro: PDB original não encontrado na pasta.")
