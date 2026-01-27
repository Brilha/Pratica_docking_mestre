import sys
import os
import numpy as np
from Bio.PDB import PDBParser

def medir_proximidade(pasta_projeto, res_inicio, res_fim):
    parser = PDBParser(QUIET=True)
    
    # Localiza os arquivos necessários na pasta
    arquivos = os.listdir(pasta_projeto)
    proteina_pdb = next((f for f in arquivos if f.endswith(".pdb") and "complexo" not in f and "pose" not in f), None)
    
    # O analisar_interacoes.py gera o melhor_pose.pdb
    ligante_pdb = os.path.join(pasta_projeto, "melhor_pose.pdb") 

    if not proteina_pdb:
        print(f"❌ Erro: Não encontrei o PDB da proteína em {pasta_projeto}")
        return
    if not os.path.exists(ligante_pdb):
        print(f"❌ Erro: Arquivo 'melhor_pose.pdb' não encontrado. Rode o analisar_interacoes.py primeiro!")
        return

    # 1. Coleta coordenadas do Motivo Alvo (HAMP)
    struct_prot = parser.get_structure('prot', os.path.join(pasta_projeto, proteina_pdb))
    coords_motivo = []
    for res in struct_prot.get_residues():
        if int(res_inicio) <= res.get_id()[1] <= int(res_fim):
            for atomo in res:
                coords_motivo.append(atomo.get_coord())
    
    if not coords_motivo:
        print(f"❌ Erro: Resíduos {res_inicio}-{res_fim} não encontrados na proteína.")
        return

    # 2. Coleta coordenadas do Ligante Dockado
    struct_lig = parser.get_structure('lig', ligante_pdb)
    coords_lig = [atomo.get_coord() for atomo in struct_lig.get_atoms()]

    # 3. Calcula os Centros Geométricos (Centroids)
    centro_motivo = np.mean(coords_motivo, axis=0)
    centro_ligante = np.mean(coords_lig, axis=0)
    
    # 4. Calcula a Distância Euclidiana entre os centros
    distancia = np.linalg.norm(centro_motivo - centro_ligante)
    
    print(f"\n{'='*50}")
    print(f"📊 RELATÓRIO DE VALIDAÇÃO DE SÍTIO")
    print(f"{'='*50}")
    print(f"📂 Projeto: {pasta_projeto}")
    print(f"📍 Motivo Alvo: {res_inicio} até {res_fim}")
    print(f"📏 Distância entre Centros: {distancia:.2f} Å")
    print(f"{'-'*50}")
    
    # Critério farmacológico de proximidade
    if distancia < 6.0:
        print("✅ SUCESSO: O fármaco se ligou EXATAMENTE no motivo alvo!")
    elif distancia < 12.0:
        print("⚠️ ALERTA: O fármaco está na periferia do sítio (ligação parcial).")
    else:
        print("❌ AFASTADO: O fármaco ignorou o motivo e ligou em outra fenda.")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python3 medir_proximidade.py <PASTA_PROJETO> <RES_INICIO> <RES_FIM>")
    else:
        medir_proximidade(sys.argv[1], sys.argv[2], sys.argv[3])