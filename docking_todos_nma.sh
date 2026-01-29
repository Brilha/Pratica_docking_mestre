#!/bin/bash

# ========================================
# docking_todos_nma.sh
# ========================================
# Executa docking iterativo em NMA
# para TODOS os ligantes
# Uso: ./docking_todos_nma.sh [--parallel]
# ========================================

set -e

CODIGOS_MESTRES="/home/brilha/bioinformatica/codigos_mestres"
SCREENING="$CODIGOS_MESTRES/screening_results"
PARALLEL=false

# Verificar flags
if [[ "$1" == "--parallel" ]]; then
    PARALLEL=true
    echo "🚀 Modo PARALELO ativado (rodará todos simultaneamente)"
fi

echo "🎯 DOCKING ITERATIVO NMA - TODOS OS LIGANTES"
echo "==========================================="
echo ""

# Verificar dependências
for cmd in vina obabel; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ Erro: $cmd não encontrado"
        echo "   Instale com: conda install -c conda-forge autodock-vina openbabel"
        exit 1
    fi
done

# Lista de ligantes
LIGANTES=(
    "ctr3_Fluconazole"
    "ctr3_Itraconazole"
    "ctr3_Metformin"
    "ctr3_Posaconazole"
    "ctr3_Voriconazole"
)

cd "$CODIGOS_MESTRES"

# Função para executar docking
executar_docking() {
    local LIGANTE=$1
    local PASTA="$SCREENING/$LIGANTE"
    
    if [ ! -d "$PASTA" ]; then
        echo "⚠️  Pasta não encontrada: $LIGANTE"
        return 1
    fi
    
    echo "🎯 Iniciando docking: $LIGANTE"
    echo "   Tempo estimado: 20-30 minutos (1 min/frame × 20)"
    
    python3 scripts/docking/docking_nma_iterativo.py "$PASTA"
    
    if [ -f "$PASTA/docking_nma_summary.json" ]; then
        echo "✅ Docking concluído: $LIGANTE"
        echo "   Resultado: $PASTA/docking_nma_summary.json"
        cat "$PASTA/docking_nma_summary.json" | python3 -m json.tool | head -10
        return 0
    else
        echo "❌ Erro ao gerar resultado: $LIGANTE"
        return 1
    fi
}

# Executar docking
if [ "$PARALLEL" = true ]; then
    echo "⚠️  Execução paralela (cuidado: alto uso de CPU/memória)"
    echo ""
    
    for LIGANTE in "${LIGANTES[@]}"; do
        executar_docking "$LIGANTE" &
    done
    
    # Aguardar todos terminarem
    wait
    echo "✅ Todos os dockings concluídos!"
else
    echo "⏳ Execução sequencial"
    echo "   (Um ligante de cada vez)"
    echo ""
    
    for LIGANTE in "${LIGANTES[@]}"; do
        echo ""
        echo "─────────────────────────────────────"
        executar_docking "$LIGANTE"
        echo "─────────────────────────────────────"
        echo ""
    done
fi

# Resumo final
echo ""
echo "=========================================="
echo "📊 RESUMO FINAL"
echo "=========================================="
echo ""
echo "Resultados disponíveis em:"
ls -1 "$SCREENING"/*/docking_nma_summary.json 2>/dev/null | while read f; do
    echo "  ✅ $(dirname $f | xargs basename)"
done

echo ""
echo "Para analisar resultados:"
echo "  cat screening_results/ctr3_*/docking_nma_summary.json | jq '.'"
