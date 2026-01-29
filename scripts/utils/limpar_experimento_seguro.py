#!/usr/bin/env python3
"""
🧹 Limpador de Experimento (Versão Segura)

Remove APENAS arquivos temporários (sem importância para resultados finais)
Preserva: relatórios, resultados, PDBs, SDFs, outputs estruturais
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def limpar_pasta_segura(pasta):
    """
    ✅ Limpar SEGURO: remove APENAS cache/temporários
    ❌ Preserva: relatórios, resultados, estruturas
    """
    
    if not os.path.exists(pasta):
        logger.error(f"❌ Pasta {pasta} não encontrada.")
        return False

    # Arquivos SEGUROS para deletar (verdadeiros temporários)
    arquivos_seguros_deletar = [
        # Extensões de log/cache
        '.log',
        '.tmp',
        '.cache',
        # Intermediários de processamento (menos críticos)
        '.out',
        '.err',
    ]
    
    # Arquivos que NUNCA devem ser deletados
    nao_deletar = [
        '.pdb',
        '.sdf', 
        '.pdbqt',
        '.html',
        '.md',
        '.txt',      # Pode conter resultados importantes
        '.png',      # Figuras de relatórios
        '.json',     # Configurações/resultados
        '.csv',      # Dados estruturados
        '.dat',      # Dados
    ]

    logger.info(f"🧹 Limpando arquivos temporários em: {pasta}")
    
    arquivos_deletados = 0
    for f in os.listdir(pasta):
        filepath = os.path.join(pasta, f)
        
        if os.path.isfile(filepath):
            # Verificar se é seguro deletar
            eh_seguro = any(f.endswith(ext) for ext in arquivos_seguros_deletar)
            tem_extensao_critica = any(f.endswith(ext) for ext in nao_deletar)
            
            if eh_seguro and not tem_extensao_critica:
                try:
                    os.remove(filepath)
                    logger.info(f"  ✅ Removido: {f}")
                    arquivos_deletados += 1
                except Exception as e:
                    logger.warning(f"  ⚠️  Erro ao remover {f}: {e}")

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Limpeza concluída!")
    logger.info(f"   Arquivos removidos: {arquivos_deletados}")
    logger.info(f"   Estruturas preservadas (PDB, SDF, outputs, relatórios)")
    logger.info(f"{'='*60}")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 limpar_experimento_seguro.py <PASTA>")
        print("Remove APENAS temporários, preserva relatórios e resultados")
        sys.exit(1)
    
    pasta = sys.argv[1]
    sucesso = limpar_pasta_segura(pasta)
    sys.exit(0 if sucesso else 1)
