"""
Detecta automaticamente se um SDF está em 2D e converte para 3D minimizado
Parte da pipeline de preparação automática
"""

import sys
import os
import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

def detectar_2d(arquivo_sdf):
    """
    ✅ Detecta se a molécula está em 2D (sem coordenadas Z significativas)
    
    Returns:
        (True, "2D") se está em 2D
        (False, "3D") se está em 3D
    """
    try:
        suppl = Chem.SDMolSupplier(arquivo_sdf, removeHs=False, sanitize=False)
        if not suppl or len(suppl) == 0:
            return None, "erro"
        
        mol = suppl[0]
        if mol is None:
            return None, "erro"
        
        # Checar se tem confômer
        if mol.GetNumConformers() == 0:
            return True, "2D"
        
        conf = mol.GetConformer()
        posicoes = conf.GetPositions()
        
        # Verificar se tem variação em Z (altura)
        z_coords = [pos[2] for pos in posicoes]
        z_min = min(z_coords)
        z_max = max(z_coords)
        z_range = abs(z_max - z_min)
        
        # Se todas as coordenadas Z são praticamente zero ou idênticas -> 2D
        if z_range < 0.01:  # Limiar muito pequeno = 2D
            return True, "2D"
        else:
            return False, "3D"
    
    except Exception as e:
        print(f"❌ Erro ao detectar 2D/3D: {e}")
        return None, "erro"

def converter_2d_para_3d(arquivo_entrada):
    """
    ✅ Converte SDF 2D para 3D com minimização de energia
    
    Retorna o caminho do arquivo convertido
    """
    nome_base = os.path.splitext(arquivo_entrada)[0]
    arquivo_saida = f"{nome_base}_3D_minimizado.sdf"
    
    print(f"[2D→3D] Detectado: Arquivo em 2D. Iniciando conversão...")
    print(f"[2D→3D] Arquivo de entrada: {arquivo_entrada}")
    print(f"[2D→3D] Arquivo de saída: {arquivo_saida}")
    
    try:
        # PASSO 1: Gerar coordenadas 3D com OpenBabel
        print(f"[2D→3D] Passo 1/2: Gerando coordenadas 3D (OpenBabel)...")
        subprocess.run([
            "obabel", arquivo_entrada, 
            "-osdf", "-O", arquivo_saida, 
            "--gen3d", "best",
            "--errorlevel", "1"
        ], check=True, capture_output=True)
        
        if not os.path.exists(arquivo_saida) or os.path.getsize(arquivo_saida) == 0:
            print(f"❌ Erro: OpenBabel gerou arquivo vazio")
            return None
        
        # PASSO 2: Minimizar energia com MMFF94
        print(f"[2D→3D] Passo 2/2: Minimizando energia (MMFF94, 500 iterações)...")
        subprocess.run([
            "obabel", arquivo_saida, 
            "-osdf", "-O", arquivo_saida, 
            "--minimize", "--steps", "500", "--ff", "MMFF94"
        ], check=True, capture_output=True)
        
        print(f"✅ [2D→3D] SUCESSO: Arquivo 3D gerado: {arquivo_saida}")
        return arquivo_saida
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao converter com OpenBabel: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return None

def processar_ligante(arquivo_sdf):
    """
    ✅ Main: Detecta se está em 2D e converte automaticamente se necessário
    
    Returns:
        Caminho do arquivo SDF a usar (original ou convertido)
    """
    print(f"\n{'='*70}")
    print(f"[2D→3D] VERIFICANDO DIMENSIONALIDADE DO SDF")
    print(f"{'='*70}")
    
    eh_2d, tipo = detectar_2d(arquivo_sdf)
    
    if eh_2d is None:
        print(f"⚠️  [2D→3D] Não foi possível determinar dimensionalidade. Usando arquivo original.")
        return arquivo_sdf
    
    if eh_2d:
        print(f"[2D→3D] 📊 Detecção: ARQUIVO EM 2D")
        arquivo_convertido = converter_2d_para_3d(arquivo_sdf)
        if arquivo_convertido:
            print(f"[2D→3D] Usando arquivo convertido: {arquivo_convertido}")
            return arquivo_convertido
        else:
            print(f"[2D→3D] Conversão falhou! Usando arquivo original (2D).")
            return arquivo_sdf
    else:
        print(f"[2D→3D] 📊 Detecção: ARQUIVO EM 3D (nenhuma conversão necessária)")
        return arquivo_sdf

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 detectar_e_converter_2d_3d.py <arquivo.sdf>")
        sys.exit(1)
    
    arquivo_sdf = sys.argv[1]
    if not os.path.exists(arquivo_sdf):
        print(f"❌ Erro: Arquivo {arquivo_sdf} não encontrado")
        sys.exit(1)
    
    resultado = processar_ligante(arquivo_sdf)
    print(f"\nArquivo a usar: {resultado}")
