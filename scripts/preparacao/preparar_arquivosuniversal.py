import os
import sys
import subprocess
from Bio.PDB import PDBParser, PDBIO, Select

try:
    from rdkit import Chem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

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

def detectar_e_converter_2d_3d(arquivo_sdf):
    """✅ NOVO: Detecta se SDF está em 2D e converte para 3D se necessário"""
    if not HAS_RDKIT:
        print(f"   -> ⚠️  RDKit não disponível. Usando SDF como está (pode ser 2D).")
        return arquivo_sdf
    
    print(f"   -> Detectando dimensionalidade do SDF...")
    try:
        suppl = Chem.SDMolSupplier(arquivo_sdf, removeHs=False, sanitize=False)
        if not suppl or len(suppl) == 0:
            print(f"   -> ⚠️  SDF vazio. Usando como está.")
            return arquivo_sdf
        
        mol = suppl[0]
        if mol is None:
            print(f"   -> ⚠️  Molécula inválida. Usando SDF como está.")
            return arquivo_sdf
        
        # Checar se tem coordenadas 3D
        if mol.GetNumConformers() == 0:
            is_2d = True
        else:
            conf = mol.GetConformer()
            posicoes = conf.GetPositions()
            z_coords = [pos[2] for pos in posicoes]
            z_range = abs(max(z_coords) - min(z_coords))
            is_2d = z_range < 0.01  # Threshold para considerar 2D
        
        if is_2d:
            print(f"   -> 📊 DETECÇÃO: SDF em 2D! Iniciando conversão para 3D...")
            nome_base = os.path.splitext(arquivo_sdf)[0]
            arquivo_3d = f"{nome_base}_3D_minimizado.sdf"
            
            try:
                # Converter para 3D com OpenBabel
                subprocess.run([
                    "obabel", arquivo_sdf, 
                    "-osdf", "-O", arquivo_3d, 
                    "--gen3d", "best", "--errorlevel", "1"
                ], check=True, capture_output=True)
                
                # Minimizar energia
                print(f"   -> Minimizando energia (MMFF94, 500 passos)...")
                subprocess.run([
                    "obabel", arquivo_3d, 
                    "-osdf", "-O", arquivo_3d, 
                    "--minimize", "--steps", "500", "--ff", "MMFF94"
                ], check=True, capture_output=True)
                
                print(f"   -> ✅ SDF 3D pronto: {arquivo_3d}")
                return arquivo_3d
            except Exception as e:
                print(f"   -> ❌ Conversão 2D→3D falhou: {e}. Usando original.")
                return arquivo_sdf
        else:
            print(f"   -> 📊 DETECÇÃO: SDF já está em 3D. Nenhuma conversão necessária.")
            return arquivo_sdf
    
    except Exception as e:
        print(f"   -> ⚠️  Erro ao detectar 2D: {e}. Usando SDF como está.")
        return arquivo_sdf

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
        # ✅ NOVO: Detectar e converter 2D→3D automaticamente
        caminho_sdf = detectar_e_converter_2d_3d(caminho_sdf)
        caminho_pdbqt = os.path.join(pasta, "ligante.pdbqt")
        converter_via_terminal(caminho_sdf, caminho_pdbqt, is_ligand=True)
    else:
        print(" [AVISO] Nenhum arquivo .sdf encontrado.")
        
    print("\n=== Preparação Concluída! ===")

