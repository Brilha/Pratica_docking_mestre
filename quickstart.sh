#!/bin/bash
# QUICK START - Virtual Screening Master
# Inicializa o ambiente refatorado com uma execução de teste

set -e

echo "======================================================================"
echo "🚀 INICIALIZANDO VIRTUAL SCREENING MASTER (REFATORADO)"
echo "======================================================================"
echo ""

cd "$(dirname "$0")"

# Verificar Python
echo "📌 Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale com: sudo apt install python3"
    exit 1
fi
echo "✅ Python 3 disponível"
echo ""

# Verificar PyYAML
echo "📌 Verificando PyYAML..."
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "⚠️  PyYAML não encontrado. Instalando..."
    pip install pyyaml
fi
echo "✅ PyYAML disponível"
echo ""

# Validar sintaxe
echo "📌 Validando sintaxe Python..."
python3 -m py_compile virtual_screening_mestre.py utils.py pipeline_step.py
echo "✅ Sintaxe validada"
echo ""

# Criar diretórios
echo "📌 Criando diretórios..."
mkdir -p logs screening_results temp
echo "✅ Diretórios criados"
echo ""

# Exibir configuração
echo "📌 Configuração Carregada:"
if [ -f config.yaml ]; then
    echo "   - Arquivo: config.yaml"
    echo "   - Alvos: $(grep -A 5 '^targets:' config.yaml | grep -oE '\- [a-zA-Z0-9_]+' | wc -l) alvos"
    echo "   - Drogas: $(grep -A 10 '^drugs:' config.yaml | grep -oE '\- [a-zA-Z0-9_]+' | wc -l) drogas"
else
    echo "❌ Arquivo config.yaml não encontrado!"
    exit 1
fi
echo ""

echo "======================================================================"
echo "✅ AMBIENTE PRONTO"
echo "======================================================================"
echo ""
echo "📖 PRÓXIMOS PASSOS:"
echo ""
echo "1️⃣  Executar screening completo:"
echo "    python3 virtual_screening_mestre.py config.yaml"
echo ""
echo "2️⃣  Modificar configuração (opcional):"
echo "    nano config.yaml"
echo ""
echo "3️⃣  Ver logs em tempo real:"
echo "    tail -f logs/screening_*.log"
echo ""
echo "4️⃣  Consultar documentação:"
echo "    cat README_REFACTORING.md"
echo ""
echo "======================================================================"
