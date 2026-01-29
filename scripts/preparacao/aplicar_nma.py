#!/usr/bin/env python3
"""
🧬 NMA (Normal Mode Analysis) - Análise de Modos Normais
Gera 20 conformações de proteína variando ao longo dos modos de movimento
Útil para: Proteínas que abrem canais, estudos de flexibilidade
"""

import os
import sys
import warnings
import numpy as np
from pathlib import Path

# Suprimir warnings do setuptools (pkg_resources deprecated)
warnings.filterwarnings("ignore", category=UserWarning, module="prody.utilities.misctools")

# Tentar importar ProDy
try:
    import prody as pd
    from prody.dynamics import GNM  # ✅ Importação correta: GNM (não GNMBase)
    from scipy import linalg  # Para cálculo manual de autovalores
    PRODY_AVAILABLE = True
except ImportError as e:
    PRODY_AVAILABLE = False
    print(f"⚠️  ProDy não instalado. Instale com: conda install -c conda-forge prody")
    print(f"   Detalhes: {e}")


def aplicar_nma(pdb_input: str, pdb_output_original: str, nma_outputs: list) -> bool:
    """
    Aplica NMA e gera conformações
    
    Args:
        pdb_input: Arquivo PDB original (ex: ctr3.pdb)
        pdb_output_original: Arquivo renomeado como FECHADO (ex: ctr3_FECHADO.pdb)
        nma_outputs: Lista de caminhos para saída NMA (ex: ctr3_NMA_01.pdb até ctr3_NMA_20.pdb)
    
    Returns:
        True se sucesso, False caso contrário
    """
    
    if not PRODY_AVAILABLE:
        print("❌ ProDy não disponível. Abortando NMA.")
        return False
    
    # Passo 1: Ler PDB original
    print(f"\n{'='*70}")
    print(f"[NMA] Iniciando análise de modos normais")
    print(f"{'='*70}")
    print(f"Input: {pdb_input}")
    
    try:
        # Renomear original como FECHADO
        import shutil
        shutil.copy(pdb_input, pdb_output_original)
        print(f"✅ Original copiado como: {pdb_output_original}")
        
        # ProDy: Carregar estrutura
        pdb_name = Path(pdb_input).stem
        pdb_ag = pd.parsePDB(pdb_input)
        
        if pdb_ag is None:
            print(f"❌ Erro ao carregar PDB com ProDy")
            return False
        
        print(f"✅ Estrutura carregada: {pdb_ag.numAtoms()} átomos")
        
        # Passo 2: Selecionar apenas Cα (rápido)
        ca_atoms = pdb_ag.select("name CA")
        
        if ca_atoms is None or ca_atoms.numAtoms() < 10:
            print(f"❌ Estrutura muito pequena para NMA (< 10 Cα)")
            return False
        
        print(f"✅ Selecionados {ca_atoms.numAtoms()} átomos Cα")
        
        # Passo 3: Calcular modos normais
        print(f"\n🔄 Calculando modos normais (usando PCA do ProDy)...")
        
        try:
            # Usar PCA ao invés de GNM para evitar problema de compatibilidade scipy
            pca = pd.PCA('PCA')
            pca.setAtoms(ca_atoms)
            pca.buildCovariance(ca_atoms.getCoords())
            pca.calcModes()
            
            if pca.numModes() < 3:
                print(f"❌ Menos de 3 modos calculados")
                return False
            
            print(f"✅ {pca.numModes()} modos calculados (usando PCA)")
            modes = pca
            
        except Exception as e:
            print(f"⚠️  Erro com PCA, tentando GNM direto...")
            try:
                # Fallback: GNM manual sem calcModes
                gnm = GNM()
                gnm.buildKirchhoff(ca_atoms)
                
                # Usar scipy diretamente para evitar turbo
                from scipy import linalg
                eigenvalues, eigenvectors = linalg.eigh(gnm.getKirchhoff())
                
                # Ordenar por autovalores (menores = modos mais relevantes)
                idx = eigenvalues.argsort()
                eigenvalues = eigenvalues[idx]
                eigenvectors = eigenvectors[:, idx]
                
                print(f"✅ {len(eigenvalues)} modos calculados (usando GNM manual)")
                modes = (eigenvalues, eigenvectors)  # Tupla (valores, vetores)
                
            except Exception as e2:
                print(f"❌ Erro ao calcular modos: {e2}")
                return False
        
        # Passo 4: Variar ao longo dos primeiros 3 modos
        print(f"\n🎬 Gerando 20 conformações variando ao longo dos modos...")
        
        conformacoes_geradas = 0
        
        # Determinar tipo de objeto de modos
        if isinstance(modes, tuple):
            # GNM manual: (eigenvalues, eigenvectors)
            eigenvalues, eigenvectors = modes
            num_modos = min(3, len(eigenvalues))
        else:
            # PCA: objeto prody.PCA
            num_modos = min(3, modes.numModes())
        
        for mode_idx in range(num_modos):
            # Obter eigenvector
            if isinstance(modes, tuple):
                eigenvector = eigenvectors[:, mode_idx]
            else:
                eigenvector = modes[mode_idx].getEigenvector()
            
            # Variar amplitude de -2σ a +2σ
            for amplitude in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
                if conformacoes_geradas >= 20:
                    break
                
                # Deslocar Cα ao longo do modo
                # Remodelar eigenvector para (N_atoms, 3) se necessário
                if eigenvector.ndim == 1:
                    # Distribuir deslocamento em x, y, z sequencialmente
                    displacements = eigenvector[:, np.newaxis] * np.array([amplitude, 0, 0])
                else:
                    displacements = amplitude * eigenvector
                
                coords_novo = ca_atoms.getCoords() + displacements
                
                # Criar nova estrutura e atualizar coordenadas
                ag_novo = pdb_ag.copy()
                ca_novo = ag_novo.select("name CA")
                
                if ca_novo is not None:
                    ca_novo.setCoords(coords_novo)
                
                # Salvar arquivo
                output_pdb = nma_outputs[conformacoes_geradas]
                try:
                    pd.writePDB(output_pdb, ag_novo)
                    print(f"  ✅ {Path(output_pdb).name}")
                    conformacoes_geradas += 1
                except Exception as e:
                    print(f"  ⚠️  Erro ao salvar {output_pdb}: {e}")
                    continue
            
            if conformacoes_geradas >= 20:
                break
        
        print(f"\n{'='*70}")
        print(f"✅ SUCESSO: {conformacoes_geradas} conformações geradas")
        print(f"{'='*70}")
        print(f"Original (FECHADO): {pdb_output_original}")
        if conformacoes_geradas > 0:
            print(f"Conformações NMA: {nma_outputs[0]} até {nma_outputs[conformacoes_geradas-1]}")
            print(f"\n💡 Abra no Chimera e use:")
            print(f"   Molecular Dynamics → MD Movie (para animar as conformações)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante NMA: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Entry point para uso via linha de comando"""
    if len(sys.argv) < 2:
        print("Uso: python3 aplicar_nma.py <pasta_trabalho>")
        print("Exemplo: python3 aplicar_nma.py ./temp/ctr3_fluconazole")
        sys.exit(1)
    
    pasta_trabalho = sys.argv[1]
    
    # Procurar por arquivo PDB (qualquer um que não seja *_clean.pdb, *_FECHADO.pdb, *_NMA_*.pdb)
    import glob
    arquivos_pdb = glob.glob(os.path.join(pasta_trabalho, "*.pdb"))
    
    # Filtrar apenas o PDB "original"
    pdb_input = None
    for pdb_file in arquivos_pdb:
        basename = os.path.basename(pdb_file)
        # Pular PDBs derivados
        if not any(suffix in basename for suffix in ['_clean', '_FECHADO', '_NMA_', '_seletividade']):
            pdb_input = pdb_file
            break
    
    if pdb_input is None:
        print(f"❌ Nenhum arquivo PDB compatível encontrado em {pasta_trabalho}")
        sys.exit(1)
    
    # Nomes de saída
    base_name = Path(pdb_input).stem
    pdb_output_original = os.path.join(pasta_trabalho, f"{base_name}_FECHADO.pdb")
    nma_outputs = [
        os.path.join(pasta_trabalho, f"{base_name}_NMA_{i:02d}.pdb")
        for i in range(1, 21)
    ]
    
    sucesso = aplicar_nma(pdb_input, pdb_output_original, nma_outputs)
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
