import os
import sys
from Bio.PDB import PDBList
import pubchempy as pcp

def criar_pasta(nome_pasta):
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
    return nome_pasta

def baixar_proteina(pdb_id, pasta_destino):
    print(f"\n--- Buscando Proteína {pdb_id} no RCSB PDB ---")
    pdbl = PDBList()
    # Baixa o arquivo .ent (formato antigo do PDB) e renomeia
    arquivo_baixado = pdbl.retrieve_pdb_file(pdb_id, pdir=pasta_destino, file_format='pdb')
    
    # O Biopython baixa com nomes estranhos (ex: pdb1a2b.ent), vamos renomear para 1a2b.pdb
    nome_final = os.path.join(pasta_destino, f"{pdb_id}.pdb")
    if os.path.exists(arquivo_baixado):
        os.rename(arquivo_baixado, nome_final)
        print(f"Sucesso: Alvo salvo em {nome_final}")
        return nome_final
    else:
        print("Erro ao baixar proteína.")
        return None

def baixar_ligante(nome_droga, pasta_destino):
    print(f"\n--- Buscando '{nome_droga}' no PubChem ---")
    try:
        # Busca a molécula pelo nome
        comps = pcp.get_compounds(nome_droga, 'name')
        
        if not comps:
            print("Erro: Droga não encontrada no PubChem.")
            return None
        
        droga = comps[0] # Pega o primeiro resultado
        nome_arquivo = os.path.join(pasta_destino, f"{nome_droga.replace(' ', '_')}.sdf")
        
        # Baixa o SDF 3D (se disponível) ou 2D
        pcp.download('SDF', nome_arquivo, droga.cid, record_type='3d', overwrite=True)
        print(f"Sucesso: Ligante (CID: {droga.cid}) salvo em {nome_arquivo}")
        return nome_arquivo
        
    except Exception as e:
        print(f"Erro no PubChem: {e}")
        return None

# --- O Main do Script ---
if __name__ == "__main__":
    print("=== AUTOMATIZADOR DE DOCKING SETUP ===")
    
    # Inputs do usuário
    alvo = input("Digite o código PDB do alvo (ex: 1BNA): ").lower()
    ligante = input("Digite o nome da droga (ex: Aspirin): ")
    
    # Cria uma pasta organizada para esse par
    nome_projeto = f"{alvo}_{ligante.replace(' ', '_')}"
    path_projeto = criar_pasta(nome_projeto)
    
    # Executa os downloads
    pdb_file = baixar_proteina(alvo, path_projeto)
    sdf_file = baixar_ligante(ligante, path_projeto)
    
    print("\n=== RESUMO ===")
    if pdb_file and sdf_file:
        print(f"Tudo pronto na pasta: {path_projeto}/")
        print("Próximos passos: Converter para PDBQT e definir Grid Box.")
    else:
        print("Algo deu errado. Verifique os nomes digitados.")
