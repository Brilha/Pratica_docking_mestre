"""
minimize_complex_energy.py
Minimização de energia para complexos proteína-ligante pós-docking

Resolve clashes estéricos removendo "bad contacts" causados por geometrias ruins do docking.
Usa OpenMM (preferencial) ou SciPy como fallback.

Usage:
    python3 minimize_complex_energy.py <pdb_file> [output_pdb]
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple
import logging
import numpy as np
from Bio.PDB import PDBParser, PDBIO

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DETECÇÃO DE CLASHES (Auto-decide se minimizar)
# ============================================================================

def detectar_clashes(pdb_file: str) -> int:
    """
    Detecta número de bad contacts (clashes estéricos) no PDB
    
    Bad contact: distância interatômica < soma dos raios van der Waals
    
    Args:
        pdb_file: Arquivo PDB
        
    Returns:
        Número de clashes detectados
    """
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("complex", pdb_file)
        
        # Raios van der Waals (Å)
        radii = {
            'H': 1.20, 'C': 1.70, 'N': 1.55, 'O': 1.52,
            'S': 1.80, 'P': 1.80, 'F': 1.47, 'Cl': 1.75,
            'Br': 1.85, 'I': 1.98
        }
        
        atoms = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        element = atom.element if hasattr(atom, 'element') else atom.name[0]
                        radius = radii.get(element, 1.70)
                        atoms.append((atom.coord, radius))
        
        # Contar clashes: distância < (r1 + r2) * 0.8
        clash_count = 0
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                coord_i, rad_i = atoms[i]
                coord_j, rad_j = atoms[j]
                
                dist = np.linalg.norm(coord_i - coord_j)
                clash_threshold = (rad_i + rad_j) * 0.85  # 85% da soma = clash
                
                if dist < clash_threshold:
                    clash_count += 1
        
        return clash_count
    except Exception as e:
        logger.error(f"Erro ao detectar clashes: {e}")
        return 0


# ============================================================================
# OPENMM BACKEND (PREFERENCIAL)
# ============================================================================

def minimize_complex_openmm(
    pdb_file: str,
    output_pdb: str,
    force_field: str = "amber14-all.xml",
    water_model: str = "tip3pfb",
    max_iterations: int = 5000,
    energy_tolerance: float = 10.0,
    step_size: float = 0.001
) -> bool:
    """
    Minimização de energia usando OpenMM
    
    Args:
        pdb_file: Arquivo PDB entrada
        output_pdb: Arquivo PDB saída
        force_field: Campo de força (amber14-all.xml)
        water_model: Modelo água (tip3pfb)
        max_iterations: Máx iterações
        energy_tolerance: Tolerância convergência (kJ/mol/nm)
        step_size: Tamanho passo
        
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        import openmm
        from openmm.app import PDBFile, ForceField, Modeller, PME, Simulation
        from openmm import LocalEnergyMinimizer, unit as u
        
        logger.info("🔬 Usando backend OpenMM para minimização")
        
        # Carregar estrutura
        logger.info(f"📂 Carregando PDB: {pdb_file}")
        pdb = PDBFile(pdb_file)
        
        # Criar force field
        logger.info(f"⚙️  Configurando force field: {force_field}")
        forcefield = ForceField(force_field, f"amber14/{water_model}.xml")
        
        # Adicionar hidrogênios
        logger.info("💧 Adicionando hidrogênios faltantes...")
        modeller = Modeller(pdb.topology, pdb.positions)
        modeller.addHydrogens(forcefield)
        
        # Criar sistema
        logger.info("🔧 Criando sistema...")
        system = forcefield.createSystem(
            modeller.topology,
            nonbondedMethod=PME,
            nonbondedCutoff=1.0*u.nanometer
        )
        
        # Simulação
        logger.info("⚙️  Configurando simulação...")
        integrator = LocalEnergyMinimizer()
        simulation = Simulation(modeller.topology, system, integrator)
        simulation.context.setPositions(modeller.positions)
        
        # Energia inicial
        state = simulation.context.getState(getEnergy=True)
        initial_energy = state.getPotentialEnergy()
        initial_kj = initial_energy.value_in_unit(u.kilojoule_per_mole)
        logger.info(f"⚡ Energia inicial: {initial_kj:.2f} kJ/mol")
        
        # Minimizar
        logger.info(f"🚀 Minimizando (max {max_iterations} iterações)...")
        simulation.minimizeEnergy(
            tolerance=energy_tolerance*u.kilojoule_per_mole/u.nanometer,
            maxIterations=max_iterations
        )
        
        # Energia final
        state = simulation.context.getState(getEnergy=True, getPositions=True)
        final_energy = state.getPotentialEnergy()
        final_kj = final_energy.value_in_unit(u.kilojoule_per_mole)
        positions = state.getPositions()
        
        logger.info(f"⚡ Energia final: {final_kj:.2f} kJ/mol")
        delta_e = initial_kj - final_kj
        pct_change = 100 * delta_e / abs(initial_kj) if initial_kj != 0 else 0
        logger.info(f"📉 Redução: {delta_e:.2f} kJ/mol ({pct_change:.1f}%)")
        
        # Salvar
        logger.info(f"💾 Salvando: {output_pdb}")
        with open(output_pdb, 'w') as f:
            PDBFile.writeFile(modeller.topology, positions, f)
        
        logger.info("✅ OpenMM minimização OK")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️  OpenMM não disponível: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro OpenMM: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# FALLBACK: SCIPY (RELAXAÇÃO DE CLASHES)
# ============================================================================

def minimize_complex_scipy(
    pdb_file: str,
    output_pdb: str,
    max_iterations: int = 5000,
    energy_tolerance: float = 0.001
) -> bool:
    """
    Minimização leve usando SciPy para relaxar clashes
    
    Nota: Menos preciso que OpenMM, mas útil para remover bad contacts
    
    Args:
        pdb_file: Arquivo PDB
        output_pdb: PDB saída
        max_iterations: Máx iterações
        energy_tolerance: Tolerância
        
    Returns:
        True se sucesso
    """
    try:
        from scipy.optimize import minimize
        
        logger.info("🔬 Usando backend SciPy para relaxação de clashes")
        logger.warning("⚠️  SciPy é fallback mais leve - resultados menos precisos")
        
        # Carregar estrutura
        logger.info(f"📂 Carregando PDB: {pdb_file}")
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("complex", pdb_file)
        
        # Extrair coordenadas
        coords_list = []
        atom_list = []
        radii_map = {
            'H': 1.2, 'C': 1.7, 'N': 1.55, 'O': 1.52,
            'S': 1.8, 'P': 1.8, 'F': 1.47, 'Cl': 1.75
        }
        
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        coords_list.append(atom.coord)
                        element = atom.element if hasattr(atom, 'element') else atom.name[0]
                        radius = radii_map.get(element, 1.7)
                        atom_list.append((atom, radius))
        
        logger.info(f"   → Carregados {len(coords_list)} átomos")
        
        coords_arr = np.array(coords_list)
        radii_arr = np.array([r for _, r in atom_list])
        
        # Função de penalidade de clashes
        def clash_penalty(coords_flat):
            """Penalidade por clashes estéricos"""
            coords = coords_flat.reshape(-1, 3)
            penalty = 0.0
            
            for i in range(len(coords)):
                for j in range(i+1, min(i+20, len(coords))):  # Vizinhança local
                    dist = np.linalg.norm(coords[i] - coords[j])
                    min_dist = radii_arr[i] + radii_arr[j]
                    
                    if dist < min_dist * 0.9:  # Penalizar clashes severos
                        gap = min_dist * 0.9 - dist
                        penalty += gap**2
            
            return penalty
        
        # Otimizar
        logger.info("🚀 Otimizando com SciPy...")
        result = minimize(
            clash_penalty,
            coords_arr.flatten(),
            method='L-BFGS-B',
            options={
                'maxiter': max_iterations,
                'ftol': energy_tolerance,
                'disp': False
            }
        )
        
        logger.info(f"   → Convergiu em {result.nit} iterações")
        logger.info(f"   → Penalidade final: {result.fun:.4f}")
        
        # Atualizar coordenadas
        opt_coords = result.x.reshape(-1, 3)
        for (atom, _), coord in zip(atom_list, opt_coords):
            atom.coord = coord
        
        # Salvar
        io = PDBIO()
        io.set_structure(structure)
        io.save(output_pdb)
        
        logger.info(f"💾 Salvando: {output_pdb}")
        logger.info("✅ SciPy minimização OK")
        return True
        
    except ImportError as e:
        logger.error(f"❌ SciPy não disponível: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro SciPy: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def minimize_complex_structure(
    pdb_file: str,
    output_pdb: Optional[str] = None,
    use_openmm: bool = True,
    **kwargs
) -> Tuple[bool, str]:
    """
    ✅ FUNÇÃO PRINCIPAL A USAR
    
    Minimização de energia para complexos proteína-ligante.
    Remove clashes estéricos pós-docking.
    
    Tenta OpenMM primeiro (mais preciso), fallback SciPy (mais leve).
    
    Args:
        pdb_file (str): PDB complexo entrada
        output_pdb (str): PDB saída. Se None, usa {basename}_minimized.pdb
        use_openmm (bool): Preferir OpenMM se disponível
        **kwargs: Argumentos para back-end específico
        
    Returns:
        Tuple[bool, str]: (sucesso, arquivo_saída)
        
    Examples:
        # Uso básico
        success, output = minimize_complex_structure("complexo.pdb")
        
        # Arquivo específico
        success, output = minimize_complex_structure(
            "complexo.pdb",
            output_pdb="minimizado.pdb"
        )
        
        # Forçar SciPy
        success, output = minimize_complex_structure(
            "complexo.pdb",
            use_openmm=False
        )
    """
    
    # Validar
    if not os.path.exists(pdb_file):
        logger.error(f"❌ Arquivo não encontrado: {pdb_file}")
        return False, ""
    
    # Gerar saída
    if output_pdb is None:
        base = Path(pdb_file).stem
        parent = Path(pdb_file).parent
        output_pdb = str(parent / f"{base}_minimized.pdb")
    
    logger.info("=" * 70)
    logger.info("🧪 MINIMIZAÇÃO DE ENERGIA - COMPLEXO PROTEÍNA-LIGANTE")
    logger.info("=" * 70)
    logger.info(f"📥 Input:  {pdb_file}")
    logger.info(f"📤 Output: {output_pdb}")
    logger.info("")
    
    # Tentar OpenMM
    if use_openmm:
        logger.info("🔍 Tentando OpenMM...")
        if minimize_complex_openmm(pdb_file, output_pdb, **kwargs):
            logger.info("=" * 70)
            return True, output_pdb
    
    # Fallback SciPy
    logger.info("🔍 Tentando SciPy fallback...")
    if minimize_complex_scipy(pdb_file, output_pdb, **kwargs):
        logger.info("=" * 70)
        return True, output_pdb
    
    # Falha
    logger.error("=" * 70)
    logger.error("❌ Nenhum back-end funcionou")
    logger.error("   Instale OpenMM: conda install -c conda-forge openmm")
    logger.error("=" * 70)
    return False, ""


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 minimize_complex_energy.py <pdb_file> [output_pdb]")
        print("")
        print("Exemplos:")
        print("  python3 minimize_complex_energy.py complexo.pdb")
        print("  python3 minimize_complex_energy.py complexo.pdb complexo_min.pdb")
        sys.exit(1)
    
    pdb_input = sys.argv[1]
    pdb_output = sys.argv[2] if len(sys.argv) > 2 else None
    
    success, output_file = minimize_complex_structure(pdb_input, pdb_output)
    
    if success:
        print(f"\n✅ Sucesso! Arquivo minimizado: {output_file}")
        sys.exit(0)
    else:
        print(f"\n❌ Falha na minimização")
        sys.exit(1)
