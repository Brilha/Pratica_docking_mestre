# 📊 Atualização: Análise de Drug-Likeness no Relatório

**Data:** 28 de Janeiro de 2026  
**Versão:** Simplificada com Análise Farmacológica Completa  
**Status:** ✅ IMPLEMENTADO E TESTADO

---

## 🎯 Resumo das Atualizações

### ✅ 1. Corrigido: Erro do RDKit
- **Problema:** Função obsoleta `SDMolBlockToMol()` não existia mais
- **Solução:** Alterado para `MolFromMolBlock()` (função atual)
- **Resultado:** Propriedades químicas agora calculadas corretamente

### ✅ 2. Simplificado: Formato do Relatório
- **Antes:** Markdown complexo com múltiplas conversões (MD → HTML)
- **Agora:** HTML direto e limpo (sem conversão intermediária)
- **Benefício:** Mais rápido, mais simples, mais confiável

### ✅ 3. Adicionado: Análise de Drug-Likeness (NOVO!)
Nova seção completa no relatório com:
- Avaliação segundo a **Regra de Lipinski**
- Verificação de 5 critérios:
  - Peso Molecular (MW) ≤ 500 Da
  - LogP (hidrofobicidade) ≤ 5
  - Doadores de H ≤ 5
  - Aceitadores de H ≤ 10
  - Ligações Rotáveis ≤ 10
- **QED Score** (Quantitative Estimate of Drug-likeness): 0-1, quanto maior melhor
- Status visual com emojis (✅, ⚠️, ❌)

---

## 📈 Estrutura Completa do Relatório

O novo relatório gera 6 seções principais:

```
📊 Relatório de Docking Molecular
│
├─ 1. Afinidade de Ligação
│  └─ Energia Vina (kcal/mol)
│
├─ 2. Propriedades Químicas
│  ├─ Peso Molecular (g/mol)
│  ├─ LogP (Hidrofobicidade)
│  ├─ H-Doadores
│  ├─ H-Aceitadores
│  ├─ Ligações Rotáveis
│  └─ QED Score
│
├─ 3. Avaliação de Drug-Likeness ⭐ NOVO!
│  ├─ Status Geral (✅ EXCELENTE / ⚠️ BOM / ❌ POBRE)
│  ├─ Tipo de Fármaco
│  ├─ Violações de Lipinski
│  └─ Análise detalhada de cada critério
│
├─ 4. Interações Proteína-Ligante (PLIP)
│  ├─ Interações Hidrofóbicas
│  ├─ Ligações de Hidrogênio
│  ├─ Pi-Stacking
│  └─ Salt Bridges
│
├─ 5. Estrutura 2D do Fármaco (se houver)
│  └─ Imagem embarcada
│
└─ 6. Arquivos Gerados
   └─ Links para todos os arquivos
```

---

## 🧬 Critérios da Regra de Lipinski

A **Regra de Lipinski** (ou Regra dos 5) prediz a possibilidade de um fármaco ser absorvido oralmente:

| Propriedade | Limite | Significado |
|-------------|--------|------------|
| **Peso Molecular** | ≤ 500 Da | Moléculas maiores têm menos permeabilidade |
| **LogP** | ≤ 5 | Hidrofobicidade controlada (≥ -2 também importa) |
| **H-Doadores** | ≤ 5 | Menos capacidade de ligação H = melhor absorção |
| **H-Aceitadores** | ≤ 10 | Idem anterior |
| **Ligações Rotáveis** | ≤ 10 | Flexibilidade molecular controlada |

**QED Score:**
- **1.0** = Fármaco ideal
- **0.5-0.8** = Fármaco promissor
- **< 0.5** = Propriedades não ideais

---

## 📝 Classificações do Fármaco

Após avaliação, a molécula recebe uma das seguintes classificações:

### ✅ EXCELENTE (0 violações)
"Fármaco promissor - Segue a Regra de Lipinski"
- Ideal para absorção oral
- Muito baixo risco farmacológico

### ⚠️ BOM (1 violação)
"Bom fármaco com 1 violação menor"
- Ainda viável
- Requer monitoramento

### ⚠️ ACEITÁVEL (2 violações)
"Potencial fármaco com algumas limitações"
- Possível, mas com restrições
- Pode depender de via alternativa

### ❌ POBRE (> 2 violações)
"Improvável de ser um bom fármaco oral"
- Não recomendado para administração oral
- Considerar alternativas

---

## 🧪 Exemplo de Saída (Voriconazole)

```
✅ EXCELENTE
Fármaco promissor - Segue a Regra de Lipinski
Violações de Lipinski: 0/5

Critérios:
✅ MW: 349.32 ≤ 500
✅ LogP: 2.18 ≤ 5
✅ H-Doadores: 1 ≤ 5
✅ H-Aceitadores: 6 ≤ 10
✅ Rotáveis: 5 ≤ 10
```

---

## 🔧 Implementação Técnica

### Função: `avaliar_drug_likeness(mol)`
Recebe uma molécula RDKit e retorna dicionário com:
- `status`: Status visual (✅/⚠️/❌)
- `classe`: Descrição do fármaco
- `violations`: Número de violações (0-5)
- `detalhes`: Lista com cada critério avaliado
- `qed`: QED Score (0-1)
- Propriedades individuais (MW, LogP, etc.)

### Função: `ler_propriedades_quimicas(pasta)`
Processa arquivo SDF e retorna HTML com:
1. Tabela de propriedades químicas
2. Caixa de análise drug-likeness

---

## 📊 Arquivos Afetados

| Arquivo | Mudança |
|---------|---------|
| `scripts/relatorio/gerar_relatorio_final.py` | ✅ Adicionadas funções de análise |
| `screening_results/*/relatorio_final.html` | ✅ Nova seção de drug-likeness |

---

## ✅ Testes Realizados

```bash
[Relatório] Processando: screening_results/test_drug
✅ Relatório salvo: screening_results/test_drug/relatorio_final.html

Resultado:
├─ Propriedades Químicas: ✅ Calculadas
├─ Drug-Likeness: ✅ Avaliado
├─ Status: ✅ EXCELENTE
└─ Violações: 0/5
```

---

## 🚀 Como Usar

O relatório é gerado automaticamente no pipeline:

```bash
python3 gerar_relatorio_final.py <pasta_resultado> [nome_droga]
```

O HTML resultante inclui **automaticamente** a análise farmacológica completa.

---

## 📚 Referências

- **Lipinski's Rule of Five** (1997)
  - Predição de drug-likeness
  - Baseado em 2000+ fármacos aprovados
  
- **QED Score** (Quantitative Estimate of Drug-likeness)
  - Desenvolvido por Bickerton et al. (2012)
  - Refinamento da Regra de Lipinski

---

**Data de Conclusão:** 28 de Janeiro de 2026  
**Status:** ✅ PRONTO PARA PRODUÇÃO
