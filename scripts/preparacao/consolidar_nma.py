#!/usr/bin/env python3
"""
Consolidar NMA em arquivo único Gromacs (.xtc)
==============================================

Converte múltiplos arquivos PDB do NMA (20 frames) em um arquivo
de trajetória única compatível com Gromacs, Chimera e PyMOL.

Formatos suportados:
- Saída: .xtc (trajetória comprimida Gromacs) ⭐ RECOMENDADO
- Saída: .gro (estrutura Gromacs)
- Entrada: .pdb (múltiplos frames)

Uso:
    python3 consolidar_nma.py <pasta_resultado> [--format xtc]
    
    Exemplos:
    - python3 consolidar_nma.py /path/to/ctr3_Fluconazole
    - python3 consolidar_nma.py screening_results/ctr3_Fluconazole --format gro
"""

import os
import sys
import glob
import logging
from pathlib import Path
from typing import List, Optional

# Try imports
try:
    from Bio.PDB import PDBParser, PDBIO, Select
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

try:
    import mdtraj as md
    HAS_MDTRAJ = True
except ImportError:
    HAS_MDTRAJ = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class NMAConsolidator:
    """Consolida múltiplos PDB do NMA em arquivo de trajetória único."""
    
    def __init__(self, resultado_path: str, output_format: str = "xtc"):
        """
        Args:
            resultado_path: Caminho da pasta com resultados (ex: screening_results/ctr3_Fluconazole)
            output_format: "xtc" (padrão) ou "gro"
        """
        self.resultado_path = Path(resultado_path)
        self.output_format = output_format.lower()
        
        if not self.resultado_path.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {self.resultado_path}")
        
        # Validar formato
        if self.output_format not in ["xtc", "gro", "dcd"]:
            raise ValueError(f"Formato inválido: {output_format}. Use 'xtc', 'gro' ou 'dcd'")
        
    def find_nma_files(self) -> List[Path]:
        """Encontra todos os arquivos NMA_*.pdb em ordem numérica."""
        nma_files = sorted(
            self.resultado_path.glob("complexo_final_NMA_*.pdb"),
            key=lambda x: int(x.stem.split("_")[-1])
        )
        
        if not nma_files:
            logger.warning(f"⚠️  Nenhum arquivo NMA encontrado em {self.resultado_path}")
            return []
        
        logger.info(f"✅ Encontrados {len(nma_files)} frames NMA")
        return nma_files
    
    def consolidate_mdtraj(self, nma_files: List[Path]) -> Path:
        """Consolida usando MDTraj (RECOMENDADO - suporta múltiplos formatos)."""
        if not HAS_MDTRAJ:
            raise ImportError("MDTraj não instalado. Instale com: pip install mdtraj")
        
        logger.info("📦 Carregando frames com MDTraj...")
        
        # Carregar primeiro frame como referência
        ref = md.load(str(nma_files[0]))
        
        # Carregar todos os frames
        trajectories = [md.load(str(f)) for f in nma_files]
        
        # Concatenar
        trajectory = trajectories[0]
        for traj in trajectories[1:]:
            trajectory = trajectory.join(traj)
        
        logger.info(f"✅ Trajetória consolidada: {len(trajectory)} frames")
        
        # Salvar
        output_file = self.resultado_path / f"complexo_NMA_completo.{self.output_format}"
        
        if self.output_format == "xtc":
            trajectory.save_xtc(str(output_file))
        elif self.output_format == "gro":
            trajectory.save_gro(str(output_file))
        elif self.output_format == "dcd":
            trajectory.save_dcd(str(output_file))
        
        logger.info(f"💾 Salvo: {output_file}")
        logger.info(f"   Tamanho: {output_file.stat().st_size / (1024*1024):.2f} MB")
        
        return output_file
    
    def consolidate_biopython(self, nma_files: List[Path]) -> Optional[Path]:
        """Fallback usando BioPython (menos versátil)."""
        if not HAS_BIOPYTHON:
            return None
        
        logger.info("📦 Carregando frames com BioPython (fallback)...")
        
        parser = PDBParser(QUIET=True)
        io = PDBIO()
        
        # Carregar todos os modelos
        structure = parser.get_structure("NMA", str(nma_files[0]))
        
        for pdb_file in nma_files[1:]:
            s = parser.get_structure("NMA", str(pdb_file))
            for model in s:
                structure.add(model)
        
        # Salvar como PDB multi-modelo
        output_file = self.resultado_path / "complexo_NMA_completo.pdb"
        io.set_structure(structure)
        io.save(str(output_file))
        
        logger.info(f"💾 Salvo (PDB multi-modelo): {output_file}")
        return output_file
    
    def create_tpr_reference(self, nma_files: List[Path]) -> None:
        """
        Cria arquivo .tpr de referência para uso com GROMACS tools.
        Requer gmx preparado previamente.
        """
        logger.info("ℹ️  Para gerar .tpr, use:")
        logger.info("  gmx editconf -f complexo_NMA_completo.gro -o complexo_NMA_completo.gro")
        logger.info("  gmx grompp -f run.mdp -c complexo_NMA_completo.gro -p topol.top -o complexo_NMA_completo.tpr")
    
    def consolidate(self) -> Path:
        """Consolida NMA - tenta MDTraj, depois BioPython."""
        nma_files = self.find_nma_files()
        
        if not nma_files:
            raise FileNotFoundError("Nenhum arquivo NMA encontrado!")
        
        # Tentar MDTraj primeiro (melhor suporte)
        if HAS_MDTRAJ:
            logger.info("🚀 Usando MDTraj para consolidação...")
            return self.consolidate_mdtraj(nma_files)
        
        # Fallback para BioPython
        if HAS_BIOPYTHON:
            logger.warning("⚠️  MDTraj não disponível, usando BioPython...")
            result = self.consolidate_biopython(nma_files)
            if result:
                return result
        
        raise RuntimeError("Instale MDTraj ou BioPython: pip install mdtraj biopython")
    
    def print_summary(self, output_file: Path) -> None:
        """Imprime resumo e instruções de uso."""
        logger.info("\n" + "="*60)
        logger.info("✅ CONSOLIDAÇÃO COMPLETA!")
        logger.info("="*60)
        logger.info(f"\n📂 Saída: {output_file}")
        logger.info(f"📊 Formato: {self.output_format.upper()}")
        logger.info(f"📦 Tamanho: {output_file.stat().st_size / (1024*1024):.2f} MB")
        
        logger.info("\n📺 Como visualizar:")
        logger.info("\n  🔵 CHIMERA (RECOMENDADO):")
        logger.info(f"    1. Abra Chimera")
        logger.info(f"    2. File → Open → {output_file.name}")
        logger.info(f"    3. MD Movie → Play")
        
        logger.info("\n  🟣 PyMOL:")
        logger.info(f"    open {output_file.name}")
        logger.info(f"    # Use 'Movie' panel para animar")
        
        logger.info("\n  🟡 GROMACS:")
        logger.info(f"    gmx trjconv -s complexo_NMA_completo.tpr -f {output_file.name} -o frame_?.pdb")
        
        logger.info("\n  💻 Discovery Studio:")
        logger.info(f"    Importar como trajetória em Projects → Trajectories")
        
        logger.info("\n💡 Dicas:")
        logger.info("  - Todos os 20 frames estão consolidados em UM arquivo")
        logger.info("  - Use o arquivo de referência (complexo_final.pdb) para grid/docking")
        logger.info("  - Para analisar movimento: Tools → Trajectory → Analyze")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    resultado_path = sys.argv[1]
    output_format = "xtc"  # padrão
    
    # Parse args
    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]
    
    try:
        consolidator = NMAConsolidator(resultado_path, output_format)
        output_file = consolidator.consolidate()
        consolidator.print_summary(output_file)
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
