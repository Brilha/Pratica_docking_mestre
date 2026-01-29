#!/usr/bin/env python3
"""
Docking Iterativo em Frames NMA
================================

Executa AutoDock Vina em cada uma das 20 conformações NMA para visualizar
como o ligante interage com a proteína em diferentes estados de abertura
do canal.

Uso:
    python3 docking_nma_iterativo.py <pasta_resultado> [--vina-path /path/to/vina]
    
    Exemplos:
    - python3 docking_nma_iterativo.py screening_results/ctr3_Fluconazole
    - python3 docking_nma_iterativo.py screening_results/ctr3_Fluconazole --vina-path ~/vina
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Tuple
import json
from datetime import datetime

try:
    from Bio.PDB import PDBParser, PDBIO, Select
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DockingNMAIterativo:
    """Executa docking em cada frame NMA."""
    
    def __init__(self, resultado_path: str, vina_path: Optional[str] = None):
        """
        Args:
            resultado_path: Caminho da pasta com resultados
            vina_path: Caminho para executável do vina
        """
        self.resultado_path = Path(resultado_path)
        
        if not self.resultado_path.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {self.resultado_path}")
        
        # Verificar instalação do Vina
        self.vina_path = self._find_vina(vina_path)
        if not self.vina_path:
            raise FileNotFoundError("AutoDock Vina não encontrado!")
        
        logger.info(f"✅ Vina encontrado: {self.vina_path}")
        
        # Carregar arquivos necessários
        self.ligante_pdbqt = self.resultado_path / "ligante.pdbqt"
        self.receptor_pdbqt = self.resultado_path / "receptor.pdbqt"
        self.config_file = self.resultado_path / "config.txt"
        self.nma_files = sorted(
            self.resultado_path.glob("complexo_final_NMA_*.pdb"),
            key=lambda x: int(x.stem.split("_")[-1])
        )
        
        # Validar
        if not self.ligante_pdbqt.exists():
            raise FileNotFoundError(f"Ligante não encontrado: {self.ligante_pdbqt}")
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config não encontrado: {self.config_file}")
        if not self.nma_files:
            raise FileNotFoundError("Nenhum arquivo NMA encontrado!")
        
        logger.info(f"✅ Arquivos validados:")
        logger.info(f"   - Ligante: {self.ligante_pdbqt.name}")
        logger.info(f"   - Config: {self.config_file.name}")
        logger.info(f"   - Frames NMA: {len(self.nma_files)}")
        
        self.results = {}
    
    def _find_vina(self, custom_path: Optional[str] = None) -> Optional[str]:
        """Localiza executável do Vina."""
        candidates = [
            custom_path,
            "/home/brilha/miniconda3/bin/vina",
            "/usr/local/bin/vina",
            "vina",
            "~/miniconda3/bin/vina"
        ]
        
        for candidate in candidates:
            if not candidate:
                continue
            candidate = os.path.expanduser(candidate)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        
        return None
    
    def pdb_to_pdbqt(self, pdb_file: Path) -> Path:
        """Converte PDB NMA para PDBQT usando mecanismo existente."""
        output = pdb_file.with_suffix(".pdbqt")
        
        # Se já existe, retorna
        if output.exists():
            return output
        
        # Tentar com obabel (mais rápido)
        try:
            cmd = ["obabel", str(pdb_file), "-O", str(output), "-p", "7.4"]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0 and output.exists():
                logger.info(f"  ✅ Convertido (obabel): {pdb_file.name} → {output.name}")
                return output
        except Exception as e:
            logger.warning(f"  ⚠️  obabel falhou: {e}")
        
        # Fallback: copiar e avisar
        logger.warning(f"  ⚠️  Não foi possível converter {pdb_file.name}")
        logger.warning(f"     Instale obabel: conda install -c conda-forge openbabel")
        raise RuntimeError(f"Falha na conversão PDB→PDBQT para {pdb_file.name}")
    
    def run_docking_frame(self, frame_num: int, nma_pdbqt: Path) -> Optional[Tuple[float, Path]]:
        """
        Executa docking de um frame específico.
        
        Returns:
            (energia_kcal_mol, arquivo_resultado_pdbqt) ou None se falhar
        """
        output_pdbqt = self.resultado_path / f"resultado_docking_NMA_{frame_num:02d}.pdbqt"
        log_file = self.resultado_path / f"log_docking_NMA_{frame_num:02d}.txt"
        
        # Se já existe, recuperar energia do log
        if output_pdbqt.exists() and log_file.exists():
            try:
                with open(log_file) as f:
                    for line in f:
                        if "BEST" in line and "kcal" in line:
                            energy = float(line.split()[1])
                            logger.info(f"  ℹ️  Frame {frame_num:02d}: Usando resultado anterior (E = {energy:.3f})")
                            return (energy, output_pdbqt)
            except:
                pass
        
        # Executar docking
        logger.info(f"  🎯 Executando docking frame {frame_num:02d}...")
        
        cmd = [
            str(self.vina_path),
            "--receptor", str(nma_pdbqt),
            "--ligand", str(self.ligante_pdbqt),
            "--config", str(self.config_file),
            "--out", str(output_pdbqt),
            "--log", str(log_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,  # 5 min por frame
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"  ❌ Vina falhou para frame {frame_num:02d}")
                logger.error(f"     STDERR: {result.stderr[:200]}")
                return None
            
            # Ler energia do resultado
            if output_pdbqt.exists():
                # Parsear PDBQT para extrair energia
                energy = self._extract_energy(output_pdbqt)
                logger.info(f"  ✅ Frame {frame_num:02d} concluído (E = {energy:.3f} kcal/mol)")
                return (energy, output_pdbqt)
            
            return None
            
        except subprocess.TimeoutExpired:
            logger.error(f"  ⏱️  Timeout no frame {frame_num:02d}")
            return None
        except Exception as e:
            logger.error(f"  ❌ Erro no docking frame {frame_num:02d}: {e}")
            return None
    
    def _extract_energy(self, pdbqt_file: Path) -> float:
        """Extrai energia de binding do arquivo PDBQT."""
        try:
            with open(pdbqt_file) as f:
                for line in f:
                    if "REMARK VINA RESULT:" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            return float(parts[3])
        except:
            pass
        return 0.0
    
    def generate_summary(self) -> None:
        """Gera sumário de energias dos dockings."""
        summary_file = self.resultado_path / "docking_nma_summary.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_frames": len(self.nma_files),
            "frames_with_results": len(self.results),
            "frames": []
        }
        
        energies = []
        for frame_num in sorted(self.results.keys()):
            energy, _ = self.results[frame_num]
            summary["frames"].append({
                "frame": frame_num,
                "energy_kcal_mol": round(energy, 3)
            })
            energies.append(energy)
        
        if energies:
            summary["statistics"] = {
                "min_energy": round(min(energies), 3),
                "max_energy": round(max(energies), 3),
                "mean_energy": round(sum(energies) / len(energies), 3),
                "best_frame": sorted(self.results.keys(), key=lambda x: self.results[x][0])[0]
            }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"💾 Sumário salvo: {summary_file}")
    
    def run_all_frames(self) -> int:
        """Executa docking em todos os frames."""
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 INICIANDO DOCKING ITERATIVO - {len(self.nma_files)} FRAMES")
        logger.info(f"{'='*60}\n")
        
        success_count = 0
        
        for i, nma_pdb in enumerate(self.nma_files, 1):
            frame_num = int(nma_pdb.stem.split("_")[-1])
            
            # Converter para PDBQT
            try:
                nma_pdbqt = self.pdb_to_pdbqt(nma_pdb)
            except Exception as e:
                logger.error(f"❌ Falha ao preparar frame {frame_num}: {e}")
                continue
            
            # Executar docking
            result = self.run_docking_frame(frame_num, nma_pdbqt)
            if result:
                self.results[frame_num] = result
                success_count += 1
            
            # Progress
            logger.info(f"Progresso: {i}/{len(self.nma_files)}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ COMPLETO: {success_count}/{len(self.nma_files)} frames com sucesso")
        logger.info(f"{'='*60}\n")
        
        # Gerar sumário
        self.generate_summary()
        
        return success_count
    
    def print_results_summary(self):
        """Imprime sumário dos resultados."""
        if not self.results:
            logger.warning("⚠️  Nenhum resultado obtido!")
            return
        
        logger.info("\n📊 RESULTADOS DO DOCKING NMA:")
        logger.info("-" * 50)
        
        energies = []
        for frame_num in sorted(self.results.keys()):
            energy, result_file = self.results[frame_num]
            energies.append(energy)
            logger.info(f"Frame {frame_num:02d}: {energy:7.3f} kcal/mol → {result_file.name}")
        
        logger.info("-" * 50)
        if energies:
            best_frame = min(self.results.keys(), key=lambda x: self.results[x][0])
            best_energy = self.results[best_frame][0]
            avg_energy = sum(energies) / len(energies)
            
            logger.info(f"Melhor frame: {best_frame:02d} ({best_energy:.3f} kcal/mol)")
            logger.info(f"Energia média: {avg_energy:.3f} kcal/mol")
            logger.info(f"Variação: {max(energies) - min(energies):.3f} kcal/mol")
        
        logger.info("\n💡 Próximos passos:")
        logger.info("1. Visualizar em Chimera:")
        logger.info(f"   Carregar: receptor_NMA_*.pdbqt + resultado_docking_NMA_*.pdbqt")
        logger.info("2. Analisar variação:")
        logger.info(f"   Ver qual frame tem melhor afinidade (menor energia)")
        logger.info("3. Comparar com NMA:")
        logger.info(f"   Correlacionar movimento proteico com preferência de ligação")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    resultado_path = sys.argv[1]
    vina_path = None
    
    # Parse args
    if "--vina-path" in sys.argv:
        idx = sys.argv.index("--vina-path")
        if idx + 1 < len(sys.argv):
            vina_path = sys.argv[idx + 1]
    
    try:
        docker = DockingNMAIterativo(resultado_path, vina_path)
        success = docker.run_all_frames()
        docker.print_results_summary()
        
        sys.exit(0 if success > 0 else 1)
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
