import sys
import os
import prolif as plf
from rdkit import Chem

def gerar_mapa_interativo(pasta_projeto):
    arquivos = os.listdir(pasta_projeto)
    proteina_pdb = next((f for f in arquivos if f.endswith(".pdb") and "complexo" not in f and "pose" not in f), None)
    ligante_pdb = os.path.join(pasta_projeto, "melhor_pose.pdb")

    if not proteina_pdb or not os.path.exists(ligante_pdb):
        print("❌ Erro: Arquivos necessários não encontrados.")
        return

    print(f"🧬 Carregando moléculas...")
    prot_mol = Chem.MolFromPDBFile(os.path.join(pasta_projeto, proteina_pdb), removeHs=False)
    lig_mol = Chem.MolFromPDBFile(ligante_pdb, removeHs=False)
    
    if not lig_mol or not prot_mol:
        print("❌ Erro: RDKit falhou na leitura.")
        return

    # Converte para moléculas ProLIF
    prot = plf.Molecule(prot_mol)
    lig = plf.Molecule(lig_mol)
    
    print(f"🔍 Mapeando interações (Método Alternativo)...")
    # Em vez de fp.run, usamos fp.generate para evitar o erro de argumentos
    fp = plf.Fingerprint()
    fp.run_from_mols([lig], prot) # Algumas versões usam run_from_mols
    
    df = fp.to_dataframe()
    if df.empty:
        print("⚠️ Nenhuma interação encontrada. O fármaco pode estar muito longe da proteína.")
        return

    net = plf.plotting.Network(df, lig_mol=lig_mol)
    output_html = os.path.join(pasta_projeto, "mapa_interativo_prolif.html")
    net.save(output_html)
    
    print(f"✅ SUCESSO: Mapa gerado em {output_html}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 gerar_mapa_prolif.py <PASTA_PROJETO>")
    else:
        gerar_mapa_interativo(sys.argv[1])