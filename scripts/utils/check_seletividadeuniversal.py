import os
import subprocess
import sys
from Bio.PDB import PDBParser, PDBIO, Select

# --- Classe para filtrar o PDB ---
class SomenteProteina(Select):
    def accept_residue(self, residue):
        # Aceita apenas aminoácidos padrão (remove HOH, ligantes e íons)
        return residue.id[0] == " "

def limpar_proteina(pdb_input, pdb_output):
    print(f"   -> Limpando proteína (Biopython)...")
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alvo", pdb_input)
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdb_output, select=SomenteProteina())
    print(f"   -> Arquivo limpo: {pdb_output}")

def converter_via_terminal(input_file, output_file, is_ligand=False):
    print(f"   -> Convertendo {input_file} via OBABEL (Sistema)...")
    
    # Monta o comando de terminal
    # -xr = mantém rigidez (bom para receptor)
    # -h = adiciona hidrogênios
    # --partialcharge gasteiger = calcula cargas
    
    cmd = ["obabel", input_file, "-O", output_file, "--partialcharge", "gasteiger"]
    
    if is_ligand:
        # Para ligante: adiciona hidrogênios (-h) e tenta gerar 3D (--gen3d) se estiver plano
        cmd.extend(["-h", "--gen3d"])
    else:
        # Para receptor: adiciona hidrogênios (-h) e trata como rígido (-xr)
        cmd.extend(["-xr", "-h"])

    # Executa o comando e captura erros se houver
    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"   -> Sucesso: {output_file} gerado.")
        else:
            print(f"   -> AVISO: Ocorreu um erro no OpenBabel:\n{resultado.stderr}")
    except FileNotFoundError:
        print("   -> ERRO CRÍTICO: O comando 'obabel' não foi encontrado. Instale com 'conda install openbabel'.")

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 check_seletividadeuniversal.py <pasta_projeto>")
        sys.exit()
        
    pasta = sys.argv[1]
    
    # Procura arquivos
    arquivos = os.listdir(pasta)
    # ✅ MODULÁVEL: Procura por qualquer PDB sem "clean" no nome (detecta automaticamente)
    pdb_file = next((f for f in arquivos if f.endswith(".pdb") and "clean" not in f and "complexo" not in f.lower() and "human" not in f.lower() and "melhor" not in f.lower()), None)
    sdf_file = next((f for f in arquivos if f.endswith(".sdf")), None)
    
    # 1. Receptor
    if pdb_file:
        raw_pdb = os.path.join(pasta, pdb_file)
        # ✅ MODULÁVEL: Nome do arquivo limpo derivado do arquivo original
        base_name = os.path.splitext(pdb_file)[0]  # Remove .pdb
        clean_pdb = os.path.join(pasta, f"{base_name}_clean.pdb")
        final_pdbqt = os.path.join(pasta, "receptor.pdbqt")
        
        limpar_proteina(raw_pdb, clean_pdb)
        converter_via_terminal(clean_pdb, final_pdbqt, is_ligand=False)
        
        # ✅ NOVO: Mantém arquivo clean para análise de seletividade
        print(f"   -> Arquivo clean preservado: {clean_pdb}")
        
    # 2. Ligante
    if sdf_file:
        raw_sdf = os.path.join(pasta, sdf_file)
        final_pdbqt = os.path.join(pasta, "ligante.pdbqt")
        converter_via_terminal(raw_sdf, final_pdbqt, is_ligand=True)

    print("\nVerifique se os arquivos .pdbqt estão na pasta agora!")