import sys
import os
import numpy as np

def calcular_grid_cego(pasta_trabalho):
    """✅ CORRIGIDO: Procura receptor.pdbqt (gerado pela preparação)"""
    
    # ✅ NOVO: Tentar receptor.pdbqt PRIMEIRO (gerado por preparar_arquivos)
    caminho_pdb = os.path.join(pasta_trabalho, "receptor.pdbqt")
    
    if not os.path.exists(caminho_pdb):
        # Fallback para receptor_tmp.pdb se PDBQT não existir
        caminho_pdb = os.path.join(pasta_trabalho, "receptor_tmp.pdb")
        if not os.path.exists(caminho_pdb):
            print(f"❌ Erro: receptor.pdbqt não encontrado em {pasta_trabalho}")
            return False

    coordenadas = []
    try:
        with open(caminho_pdb, 'r') as f:
            for linha in f:
                if linha.startswith(("ATOM", "HETATM")):
                    try:
                        x = float(linha[30:38])
                        y = float(linha[38:46])
                        z = float(linha[46:54])
                        coordenadas.append([x, y, z])
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    if not coordenadas:
        print(f"❌ Erro: Nenhuma coordenada encontrada em {caminho_pdb}")
        return False

    coords = np.array(coordenadas)
    centro = coords.mean(axis=0)
    # Calcula a extensão da proteína para cobri-la inteira
    dimensoes = coords.max(axis=0) - coords.min(axis=0) + 10.0  # Margem de segurança

    output = os.path.join(pasta_trabalho, "config.txt")
    try:
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
        
        print(f"✅ SUCESSO: Arquivo 'config.txt' gerado na pasta.")
        print(f"   Centro Proteína: ({centro[0]:.3f}, {centro[1]:.3f}, {centro[2]:.3f})")
        print(f"   Dimensões Caixa: ({dimensoes[0]:.3f}, {dimensoes[1]:.3f}, {dimensoes[2]:.3f})")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao escrever arquivo: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sucesso = calcular_grid_cego(sys.argv[1])
        sys.exit(0 if sucesso else 1)
    else:
        print("❌ Uso: python3 definir_grid_cego.py <pasta_trabalho>")
        sys.exit(1)