#!/usr/bin/env python3
"""
minimize_complex_energy_wrapper.py

Wrapper simplificado para uso no pipeline do virtual screening.
Minimiza complexo proteína-ligante para remover clashes pós-docking.

Uso:
    python3 minimize_complex_energy_wrapper.py <pasta_projeto>

Procura por 'complexo_final.pdb' em <pasta_projeto> e gera
'complexo_final_minimized.pdb' no mesmo diretório.
"""

import sys
import os
from pathlib import Path

# Import da função principal
from minimize_complex_energy import minimize_complex_structure, logger


def processar_pasta_projeto(pasta_projeto: str) -> bool:
    """
    Processa uma pasta de projeto, minimizando o complexo final.
    
    Args:
        pasta_projeto: Caminho da pasta contendo os arquivos
        
    Returns:
        True se sucesso, False caso contrário
    """
    
    pasta = Path(pasta_projeto)
    
    if not pasta.exists():
        logger.error(f"❌ Pasta não encontrada: {pasta_projeto}")
        return False
    
    # Procurar complexo_final.pdb
    complexo_final = pasta / "complexo_final.pdb"
    
    if not complexo_final.exists():
        logger.error(f"❌ Arquivo não encontrado: {complexo_final}")
        logger.info("   Procurando por 'complexo_final.pdb' na pasta")
        return False
    
    # Definir saída
    complexo_minimizado = pasta / "complexo_final_minimized.pdb"
    
    logger.info(f"🎯 Processando pasta: {pasta}")
    logger.info(f"   Input:  {complexo_final.name}")
    logger.info(f"   Output: {complexo_minimizado.name}")
    logger.info("")
    
    # Minimizar
    success, output_file = minimize_complex_structure(
        str(complexo_final),
        output_pdb=str(complexo_minimizado)
    )
    
    if success:
        logger.info(f"\n✅ Complexo minimizado com sucesso!")
        logger.info(f"   Arquivo: {output_file}")
        return True
    else:
        logger.error(f"\n❌ Falha ao minimizar complexo")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 minimize_complex_energy_wrapper.py <pasta_projeto>")
        print("")
        print("Exemplo:")
        print("  python3 minimize_complex_energy_wrapper.py screening_results/ctr3_Fluconazole")
        print("")
        print("Procura por: screening_results/ctr3_Fluconazole/complexo_final.pdb")
        print("Gera:        screening_results/ctr3_Fluconazole/complexo_final_minimized.pdb")
        sys.exit(1)
    
    pasta = sys.argv[1]
    success = processar_pasta_projeto(pasta)
    
    sys.exit(0 if success else 1)
