#!/bin/bash

# ========================================
# consolidar_todos_nma.sh
# ========================================
# Consolida NMA para TODOS os ligantes
# Uso: ./consolidar_todos_nma.sh
# ========================================

set -e  # Exit on error

CODIGOS_MESTRES="/home/brilha/bioinformatica/codigos_mestres"
SCREENING="$CODIGOS_MESTRES/screening_results"

echo "🔬 CONSOLIDAÇÃO DE NMA - TODOS OS LIGANTES"
echo "=========================================="
echo ""

# Verificar se MDTraj está instalado
if ! python3 -c "import mdtraj" 2>/dev/null; then
    echo "❌ Erro: MDTraj não encontrado"
    echo "   Instale com: pip install mdtraj"
    exit 1
fi

# Lista de ligantes
LIGANTES=(
    "ctr3_Fluconazole"
    "ctr3_Itraconazole"
    "ctr3_Metformin"
    "ctr3_Posaconazole"
    "ctr3_Voriconazole"
)

# Contadores
TOTAL=${#LIGANTES[@]}
SUCESSO=0
ERRO=0

cd "$CODIGOS_MESTRES"

# Iterar sobre cada ligante
for LIGANTE in "${LIGANTES[@]}"; do
    PASTA="$SCREENING/$LIGANTE"
    
    if [ ! -d "$PASTA" ]; then
        echo "⚠️  Pasta não encontrada: $PASTA"
        ((ERRO++))
        continue
    fi
    
    echo "📦 Consolidando: $LIGANTE"
    
    # Executar consolidação
    if python3 scripts/preparacao/consolidar_nma.py "$PASTA" --format xtc 2>&1 | tail -3; then
        ((SUCESSO++))
        echo "   ✅ OK"
    else
        ((ERRO++))
        echo "   ❌ ERRO"
    fi
    
    echo ""
done

# Resumo
echo "=========================================="
echo "📊 RESUMO"
echo "=========================================="
echo "Total de ligantes: $TOTAL"
echo "✅ Sucesso: $SUCESSO"
echo "❌ Erros: $ERRO"
echo ""

# Listar arquivos criados
echo "📂 Arquivos criados:"
echo "=========================================="
ls -lh "$SCREENING"/*/complexo_NMA_completo.xtc 2>/dev/null || echo "Nenhum arquivo encontrado"

echo ""
echo "✅ Consolidação completa!"
echo ""
echo "Próximo passo: Visualizar em CHIMERA"
echo "  chimera screening_results/ctr3_Fluconazole/complexo_final.pdb \\"
echo "          screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc"
