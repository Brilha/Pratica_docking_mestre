# 📖 ÍNDICE CENTRAL - Virtual Screening Pipeline (Versão Final)

**Data:** 28 de Janeiro de 2026  
**Versão:** Final - Consolidado e Otimizado  
**Ênfase:** NMA é crítico e pode ser executado SEPARADAMENTE

---

## ⚡ Comece Aqui (1-2 minutos)

### Se você quer executar NMA agora:
👉 **[GUIA_NMA_COMPLETO.md](GUIA_NMA_COMPLETO.md)** ⭐ **COMECE AQUI**
- Como rodar NMA (2 métodos)
- Como consolidar em 1 arquivo
- Como visualizar
- Pronto para usar

### Se você quer entender o pipeline completo:
👉 **[RESUMO_PHASE5.md](RESUMO_PHASE5.md)** 
- O que foi implementado (Phase 5)
- Quick start (5 minutos)
- Scripts prontos para usar

### Se você quer análise de seletividade:
👉 **[GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md)**
- Análise completa para Chimera, PyMOL, Discovery Studio
- Passo-a-passo detalhado
- Interpretação de resultados

---

## 🚀 Documentação Principal (9 documentos essenciais)

| # | Documento | Tipo | Quando Usar |
|---|-----------|------|------------|
| 1 | **[GUIA_NMA_COMPLETO.md](GUIA_NMA_COMPLETO.md)** | 🧬 Tutorial | Gerar + consolidar + analisar NMA |
| 2 | **[AUDITORIA_SCRIPTS_JAN28.md](AUDITORIA_SCRIPTS_JAN28.md)** | 🧹 Arquitetura | Estrutura limpa e 100% modular |
| 3 | **[BLAST_LOCAL_CORRECAO.md](BLAST_LOCAL_CORRECAO.md)** | ✅ Correção | BLAST local implementado (1-2 seg) |
| 4 | **[RESUMO_PHASE5.md](RESUMO_PHASE5.md)** | 📋 Quick Start | Overview do pipeline (5 min) |
| 5 | **[GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md)** | 📊 Análise | Analisar seletividade (toxicidade) |
| 6 | **[DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)** | 📚 Referência | Documentação completa de tudo |
| 7 | **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | 🆘 Problemas | Resolver erros e dúvidas |
| 8 | **[ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md)** | ⚙️ Técnico | Detalhes técnicos de Phase 5 |
| 9 | **[WELCOME.txt](WELCOME.txt)** | 👋 Info | Boas-vindas + estrutura do projeto |

---

## 📖 Como Navegar

### 🧬 Quer aprender sobre NMA?
1. [GUIA_NMA_COMPLETO.md](GUIA_NMA_COMPLETO.md) - Tudo sobre NMA
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Se der erro

### 🚀 Quer rodar o pipeline completo?
1. [RESUMO_PHASE5.md](RESUMO_PHASE5.md) - Overview rápido
2. [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) - Detalhes completos

### 📊 Quer analisar resultados?
1. [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md) - Seletividade + análise
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Dúvidas

### 🔧 Quer entender o código?
1. [AUDITORIA_SCRIPTS_JAN28.md](AUDITORIA_SCRIPTS_JAN28.md) - Estrutura e modularidade
2. [ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md) - Detalhes técnicos
3. [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) - Documentação completa

---

## 📚 Documentação por Tópico

### 🚀 Phase 5 (NOVO!)

| Documento | Conteúdo |
|-----------|----------|
| [RESUMO_PHASE5.md](RESUMO_PHASE5.md) | **Comece aqui** - O que foi implementado |
| [ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md) | Detalhes técnicos de cada adição |
| [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md) | Análise completa de seletividade |

### 📖 Documentação Principal

| Documento | Conteúdo |
|-----------|----------|
| [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) | Documentação do projeto inteiro (Phases 1-5) |
| [NOVAS_FUNCIONALIDADES.md](NOVAS_FUNCIONALIDADES.md) | Histórico de funcionalidades por phase |
| [RESUMO_LIMPEZA.md](RESUMO_LIMPEZA.md) | Histórico de limpeza de código |

### ⚙️ Configuração

| Arquivo | Propósito |
|---------|----------|
| [config.yaml](config.yaml) | Configuração principal do pipeline |
| [config.py](config.py) | Loader de YAML em Python |

---

## 🛠️ Scripts por Categoria

### 📋 Preparação de Estruturas

```
scripts/preparacao/
├── preparar_arquivos_universal.py          # Preparação básica (PDB, PDBQT)
├── detectar_e_converter_2d_3d.py           # Detecta e converte SDF 2D→3D
├── aplicar_nma.py                          # NMA (Normal Mode Analysis)
└── consolidar_nma.py                       # ⭐ NOVO - Consolida 20 frames em 1
```

### 🎯 Docking

```
scripts/docking/
├── gridbox.py                              # Preparação de grid
├── grid_cego.py                            # Grid cego (whole protein)
├── rodar_docking.py                        # Docking com Vina
└── docking_nma_iterativo.py               # ⭐ NOVO - Docking em 20 frames
```

### 🔍 Análise

```
scripts/analise/
├── analise_quimica_completa.py             # Análise de propriedades químicas
├── rodar_plip.py                           # PLIP (interações proteína-ligante)
└── rodar_prolif.py                         # ProLIF (fingerprints)
```

### 🧬 Seletividade

```
scripts/utils/
├── check_seletividade_universal.py         # BLAST contra proteína humana
├── cor_pdb_seletividade.py                 # Colore por B-factor (seletividade)
└── ... (utilitários)
```

### 📊 Relatórios

```
scripts/relatorio/
├── gerar_relatorio.py                      # Gera HTML/MD com resultados
└── ... (análises de relatório)
```

---

## 🎬 Workflows Recomendados

### Workflow Completo (Primeiro uso)

```
1. Executar pipeline base
   python3 virtual_screening_mestre.py config.yaml
   
2. Consolidar NMA (novo)
   cd screening_results/ctr3_Fluconazole
   python3 ../../scripts/preparacao/consolidar_nma.py . --format xtc
   
3. Docking iterativo (novo)
   python3 ../../scripts/docking/docking_nma_iterativo.py .
   
4. Analisar seletividade
   Consulte GUIA_SELETIVIDADE_NMAANALISE.md
```

### Análise de Seletividade apenas

```
→ Consulte [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md)
  Inclui: Chimera, PyMOL, Discovery Studio
```

### NMA + Docking

```
1. consolidar_nma.py → .xtc para visualização
2. docking_nma_iterativo.py → docking_nma_summary.json
3. Comparar energias e frames
```

---

## 📂 Estrutura de Pastas

```
/home/brilha/bioinformatica/codigos_mestres/
│
├── 📄 Documentação (Leia em ordem!)
│   ├── README.md (se existir)
│   ├── RESUMO_PHASE5.md ⭐ COMECE AQUI
│   ├── DOCUMENTACAO_COMPLETA.md
│   ├── GUIA_SELETIVIDADE_NMAANALISE.md ⭐ NOVO
│   ├── ATUALIZACOES_PHASE5.md ⭐ NOVO
│   ├── NOVAS_FUNCIONALIDADES.md
│   ├── RESUMO_LIMPEZA.md
│   ├── INDEX.md ← Você está aqui
│   └── QUICKSTART.sh
│
├── ⚙️ Configuração
│   ├── config.yaml
│   ├── config.py
│   ├── config/targets.json
│   ├── config/drugs.json
│   └── config/...
│
├── 🐍 Scripts Principais
│   ├── virtual_screening_mestre.py
│   ├── pipeline_step.py
│   ├── utils.py
│   └── scripts/
│       ├── preparacao/
│       │   ├── preparar_arquivos_universal.py
│       │   ├── detectar_e_converter_2d_3d.py
│       │   ├── aplicar_nma.py
│       │   └── consolidar_nma.py ⭐ NOVO
│       │
│       ├── docking/
│       │   ├── gridbox.py
│       │   ├── grid_cego.py
│       │   ├── rodar_docking.py
│       │   └── docking_nma_iterativo.py ⭐ NOVO
│       │
│       ├── analise/
│       │   ├── analise_quimica_completa.py
│       │   ├── rodar_plip.py
│       │   └── rodar_prolif.py
│       │
│       ├── utils/
│       │   ├── check_seletividade_universal.py
│       │   ├── cor_pdb_seletividade.py
│       │   └── ...
│       │
│       └── relatorio/
│           ├── gerar_relatorio.py
│           └── ...
│
├── 📦 Templates (Referências e Input)
│   ├── proteins/
│   │   └── *.pdb
│   ├── drugs/
│   │   └── *.sdf
│   └── proteinas_humanas/
│       └── *.pdb (para seletividade)
│
├── 📊 Resultados
│   ├── Teste_ctr3/
│   ├── Teste_atpsintased/
│   └── screening_results/
│       └── ctr3_Fluconazole/
│           ├── complexo_final_NMA_01.pdb ... NMA_20.pdb (20 frames)
│           ├── complexo_NMA_completo.xtc ⭐ NOVO (output consolidar_nma)
│           ├── resultado_docking_NMA_01.pdbqt ... NMA_20.pdbqt ⭐ NOVO (output docking iterativo)
│           ├── docking_nma_summary.json ⭐ NOVO (análise de energias)
│           ├── relatorio_final.html
│           └── ...
│
└── 📝 Logs e Temporários
    ├── logs/
    └── ...
```

---

## 📖 Leitura por Caso de Uso

### "Quero entender o que foi adicionado agora"
→ [RESUMO_PHASE5.md](RESUMO_PHASE5.md) (5 min leitura)

### "Quero usar os 2 novos scripts"
→ [ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md) (seção "Quick Start Phase 5")

### "Quero analisar seletividade"
→ [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md) (completo)

### "Quero entender o arquivo .pse"
→ [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md) (seção "Arquivo .pse")

### "Quero aprender o pipeline completo"
→ [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) (completo, 1 hora)

### "Tenho um erro"
→ [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) (seção Troubleshooting)

### "Quero ver histórico de mudanças"
→ [NOVAS_FUNCIONALIDADES.md](NOVAS_FUNCIONALIDADES.md) ou [RESUMO_LIMPEZA.md](RESUMO_LIMPEZA.md)

---

## 🎯 Checklists Rápidos

### ✅ Preparação Inicial
- [ ] Python 3.7+ instalado
- [ ] pip install biopython rdkit openbabel pyyaml requests
- [ ] AutoDock Vina em PATH (vina)
- [ ] ProDy instalado (para NMA): pip install prody
- [ ] MDTraj instalado (para consolidar): pip install mdtraj

### ✅ Primeiro Pipeline
- [ ] Configurar config.yaml com targets e drugs
- [ ] Colocar proteínas humanas em templates/proteinas_humanas/
- [ ] Executar: python3 virtual_screening_mestre.py config.yaml
- [ ] Selecionar "aplicar_nma" no menu

### ✅ Phase 5 (Novo!)
- [ ] Leu [RESUMO_PHASE5.md](RESUMO_PHASE5.md)
- [ ] Executou: consolidar_nma.py
- [ ] Executou: docking_nma_iterativo.py
- [ ] Visualizou em Chimera/PyMOL
- [ ] Consultou [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md)

---

## 🔗 Links Rápidos

### Scripts (Use assim)
```bash
# Consolidar NMA
python3 scripts/preparacao/consolidar_nma.py <pasta>

# Docking iterativo
python3 scripts/docking/docking_nma_iterativo.py <pasta>

# Pipeline completo
python3 virtual_screening_mestre.py config.yaml
```

### Documentação (Leia assim)
- 📖 [RESUMO_PHASE5.md](RESUMO_PHASE5.md) ← Mais importante agora
- 📖 [DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md) ← Tudo
- 📖 [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md) ← Análise detalhada

---

## ✨ Novidades Phase 5

| Item | Localização | Status |
|------|-------------|--------|
| consolidar_nma.py | scripts/preparacao/ | ✅ Criado |
| docking_nma_iterativo.py | scripts/docking/ | ✅ Criado |
| GUIA_SELETIVIDADE_NMAANALISE.md | Raiz | ✅ Criado |
| ATUALIZACOES_PHASE5.md | Raiz | ✅ Criado |
| RESUMO_PHASE5.md | Raiz | ✅ Criado |
| INDEX.md (este arquivo) | Raiz | ✅ Criado |

---

## 🆘 Ajuda Rápida

**"Onde começo?"**
→ Leia [RESUMO_PHASE5.md](RESUMO_PHASE5.md)

**"Como uso consolidar_nma?"**
→ Veja [ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md#️⃣-script-consolidar_nmappy)

**"Como uso docking_nma_iterativo?"**
→ Veja [ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md#️⃣-script-docking_nma_iterativopy)

**"Como analisar seletividade?"**
→ Leia [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md)

**"Tenho erro no script?"**
→ Veja [ATUALIZACOES_PHASE5.md](ATUALIZACOES_PHASE5.md#-troubleshooting)

---

## 📊 Estatísticas do Projeto

```
Documentação:     6 arquivos principais
Scripts novos:    2 (consolidar_nma + docking_nma_iterativo)
Scripts totais:   15+ scripts funcionais
Linhas de código: ~5000+ linhas
Phases:           5 completas
Status:           ✅ Production-Ready
```

---

## 📞 Próximos Passos

1. **Leia:** [RESUMO_PHASE5.md](RESUMO_PHASE5.md) (5 minutos)
2. **Execute:** consolidar_nma.py (30 segundos)
3. **Analise:** docking_nma_summary.json (imediato)
4. **Visualize:** em Chimera/PyMOL (5 minutos)
5. **Estude:** [GUIA_SELETIVIDADE_NMAANALISE.md](GUIA_SELETIVIDADE_NMAANALISE.md) (30 minutos)

---

**Desenvolvido por:** GitHub Copilot  
**Data:** 28 de Janeiro de 2026  
**Versão:** 5.0  
**Status:** ✅ Production-Ready

Próximo passo: Leia [RESUMO_PHASE5.md](RESUMO_PHASE5.md) 👉
