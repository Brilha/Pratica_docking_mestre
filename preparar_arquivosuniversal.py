import os
import sys
import subprocess
from Bio.PDB import PDBParser, PDBIO, Select

# --- Classe para filtrar o PDB (Biopython) ---
class SomenteProteina(Select):
    def accept_residue(self, residue):
        # Aceita apenas aminoácidos (remove águas HOH e ligantes HETATM)
        return residue.id[0] == " "

def limpar_proteina(pdb_input, pdb_output):
    print(f"   -> Limpando proteína (Biopython)...")
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alvo", pdb_input)
    
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdb_output, select=SomenteProteina())
    print(f"   -> Arquivo limpo salvo em: {pdb_output}")

def converter_via_terminal(input_file, output_file, is_ligand=False):
    print(f"   -> Convertendo {input_file} via OBABEL (Sistema)...")
    
    # Monta o comando do terminal
    cmd = ["obabel", input_file, "-O", output_file, "--partialcharge", "gasteiger"]
    
    if is_ligand:
        # Se for ligante: adiciona hidrogênios (-h) e gera 3D (--gen3d)
        cmd.extend(["-h", "--gen3d"])
    else:
        # Se for receptor: adiciona hidrogênios (-h) e trata como rígido (-xr)
        cmd.extend(["-xr", "-h"])

    try:
        # Executa o comando
        resultado = subprocess.run(cmd, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print(f"   -> Conversão base concluída: {output_file}")
            
            # --- CORREÇÃO AUTOMÁTICA PARA RECEPTOR ---
            if not is_ligand:
                print("   -> Removendo tags proibidas (ROOT/BRANCH) do receptor...")
                subprocess.run(["sed", "-i", "/ROOT/d", output_file])
                subprocess.run(["sed", "-i", "/BRANCH/d", output_file])
                subprocess.run(["sed", "-i", "/TORSDOF/d", output_file])
                print("   -> Receptor pronto para o Vina.")
        else:
            print(f"   -> AVISO DE ERRO NO OBABEL:\n{resultado.stderr}")
            
    except FileNotFoundError:
        print("   -> ERRO CRÍTICO: O comando 'obabel' não foi encontrado. Instale com 'conda install openbabel'.")

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 preparar_arquivos.py <nome_da_pasta_projeto>")
        sys.exit()
        
    pasta = sys.argv[1]
    if not os.path.exists(pasta):
        print("Pasta não encontrada!")
        sys.exit()

    print(f"=== PREPARANDO ARQUIVOS NA PASTA: {pasta} ===")
    
    # Varre a pasta procurando PDB e SDF
    arquivos = os.listdir(pasta)
    pdb_file = next((f for f in arquivos if f.endswith(".pdb") and "clean" not in f), None)
    sdf_file = next((f for f in arquivos if f.endswith(".sdf")), None)
    
    # 1. Processar Proteína
    if pdb_file:
        caminho_pdb = os.path.join(pasta, pdb_file)
        caminho_clean = os.path.join(pasta, "receptor_tmp.pdb") # Temporário
        caminho_pdbqt = os.path.join(pasta, "receptor.pdbqt")
        
        # Limpa (Biopython) e depois Converte (Terminal)
        limpar_proteina(caminho_pdb, caminho_clean)
        converter_via_terminal(caminho_clean, caminho_pdbqt, is_ligand=False)
        
        # Remove o arquivo temporário
        if os.path.exists(caminho_clean):
            os.remove(caminho_clean)
            
    else:
        print(" [AVISO] Nenhum arquivo .pdb encontrado.")

    # 2. Processar Ligante
    if sdf_file:
        caminho_sdf = os.path.join(pasta, sdf_file)
        caminho_pdbqt = os.path.join(pasta, "ligante.pdbqt")
        converter_via_terminal(caminho_sdf, caminho_pdbqt, is_ligand=True)
    else:
        print(" [AVISO] Nenhum arquivo .sdf encontrado.")
        
    print("\n=== Preparação Concluída! ===")
