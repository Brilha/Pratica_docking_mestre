# 🧬 GUIA COMPLETO: NMA (Normal Mode Analysis) - CRÍTICO

**Data:** 28 de Janeiro de 2026  
**Versão:** 2.0 - Consolidado e Simplificado  
**Ênfase:** Você pode rodar NMA SEPARADAMENTE em qualquer momento

---

## 📋 Índice Rápido

1. [O que é NMA?](#o-que-é)
2. [Rodar NMA pelo Master Script](#rodar-nma-master)
3. [Rodar NMA Separadamente (IMPORTANTE)](#rodar-nma-separado)
4. [Consolidar 20 Frames em 1 Arquivo](#consolidar-frames)
5. [Visualizar Animação](#visualizar)
6. [Docking Iterativo em NMA](#docking-nma)
7. [Troubleshooting](#troubleshooting)

---

## 🧬 O que é NMA? {#o-que-é}

**NMA** = Normal Mode Analysis (Análise de Modos Normais)

### Por que usar?

```
Seu canal pode abrir e fechar de diferentes formas.
NMA gera 20 conformações diferentes mostrando esses movimentos.

Benefícios:
✅ Vê como o ligante interage em CADA conformação
✅ Identifica melhor frame para docking
✅ Entende movimento do canal
✅ Melhora precisão do docking
```

### O que você recebe

```
NMA gera:
├─ 20 arquivos PDB (complexo_final_NMA_01.pdb até NMA_20.pdb)
├─ Cada um com conformação diferente da proteína
└─ Com ligante já presente (posição inicial)
```

---

## 🚀 Método 1: Rodar NMA pelo Master Script {#rodar-nma-master}

Se você **NÃO** ativou NMA durante o master script, pode ativar depois!

### Passo 1: Rodar o Master Script

```bash
cd /home/brilha/bioinformatica/codigos_mestres

python3 virtual_screening_mestre.py config.yaml
```

### Passo 2: Quando pedir scripts opcionais, escolha NMA

Quando aparecer:

```
📋 SCRIPTS OPCIONAIS DISPONÍVEIS

5. [ADVANCED] aplicar_nma
   NMA: Gera 20 conformações de modos normais
   
✏️  Quais passos opcionais deseja ativar? → 5
```

### Resultado esperado

```bash
✅ 20 arquivos PDB criados:
   screening_results/ctr3_Fluconazole/complexo_final_NMA_01.pdb
   screening_results/ctr3_Fluconazole/complexo_final_NMA_02.pdb
   ...
   screening_results/ctr3_Fluconazole/complexo_final_NMA_20.pdb
```

---

## 🎯 Método 2: Rodar NMA Separadamente (RECOMENDADO) {#rodar-nma-separado}

### Por que rodar separadamente?

✅ **Você pode rodar com QUALQUER ligante + proteína**  
✅ **Sem precisar rodar todo o pipeline**  
✅ **Em qualquer momento**  
✅ **Muito mais rápido**

### Passo 1: Preparar Arquivos

Você precisa de:
- `complexo_final.pdb` - Arquivo do docking (proteína + ligante)
- Estar em uma pasta de resultado (ou criar uma)

**Exemplo 1: Usar resultado já existente**

```bash
cd /home/brilha/bioinformatica/codigos_mestres/screening_results/ctr3_Fluconazole

# Verificar se complexo_final.pdb existe
ls -lah complexo_final.pdb
```

**Exemplo 2: Criar nova pasta para NMA customizado**

```bash
cd /home/brilha/bioinformatica/codigos_mestres/screening_results

# Criar pasta
mkdir nova_analise_fluconazole

# Copiar arquivo de docking
cp ctr3_Fluconazole/complexo_final.pdb nova_analise_fluconazole/

# Entrar na pasta
cd nova_analise_fluconazole
```

### Passo 2: Executar NMA

```bash
# Opção A: Linha de comando simples
python3 ../../scripts/preparacao/aplicar_nma.py .

# Opção B: Com mais detalhes
python3 ../../scripts/preparacao/aplicar_nma.py . --verbose

# Opção C: Com número de frames customizado (padrão é 20)
python3 ../../scripts/preparacao/aplicar_nma.py . --nframes 15
```

### Passo 3: Verificar Resultado

```bash
# Listar frames gerados
ls -lah complexo_final_NMA_*.pdb

# Esperado:
# -rw-r--r-- 1 brilha brilha 121K Jan 28 17:10 complexo_final_NMA_01.pdb
# -rw-r--r-- 1 brilha brilha 121K Jan 28 17:10 complexo_final_NMA_02.pdb
# ...
# -rw-r--r-- 1 brilha brilha 121K Jan 28 17:10 complexo_final_NMA_20.pdb

# Contar frames
ls -1 complexo_final_NMA_*.pdb | wc -l
# Esperado: 20
```

### Exemplo Prático Completo

```bash
#!/bin/bash
# Rodar NMA para todos os ligantes

cd /home/brilha/bioinformatica/codigos_mestres/screening_results

for ligante in ctr3_*; do
    echo "🧬 Gerando NMA para $ligante..."
    cd "$ligante"
    
    # Se já tiver NMA, pula
    if [ ! -f complexo_final_NMA_01.pdb ]; then
        python3 ../../scripts/preparacao/aplicar_nma.py .
    else
        echo "   ✅ NMA já existe"
    fi
    
    cd ..
done

echo "✅ NMA gerado para todos os ligantes"
```

---

## 📦 Consolidar 20 Frames em 1 Arquivo {#consolidar-frames}

Depois de gerar os 20 frames, consolide em um arquivo único para **animação fluida**.

### Por que consolidar?

```
❌ 20 PDBs separados = Difícil animar
✅ 1 arquivo .xtc   = Animação fluida em CHIMERA/PyMOL
```

### Consolidação Manual (1 arquivo específico)

```bash
cd /home/brilha/bioinformatica/codigos_mestres

# Para um ligante específico
python3 scripts/preparacao/consolidar_nma.py \
    screening_results/ctr3_Fluconazole \
    --format xtc

# Resultado:
# ✅ screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc (0.12 MB)
```

### Consolidação Automática (TODOS os ligantes)

```bash
cd /home/brilha/bioinformatica/codigos_mestres

# Script pronto - consolida os 5 ligantes
./consolidar_todos_nma.sh

# Resultado:
# ✅ screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc
# ✅ screening_results/ctr3_Itraconazole/complexo_NMA_completo.xtc
# ✅ screening_results/ctr3_Metformin/complexo_NMA_completo.xtc
# ✅ screening_results/ctr3_Posaconazole/complexo_NMA_completo.xtc
# ✅ screening_results/ctr3_Voriconazole/complexo_NMA_completo.xtc
```

### Formatos Disponíveis

```bash
# .xtc (padrão - mais compacto)
python3 scripts/preparacao/consolidar_nma.py <pasta> --format xtc

# .gro (alternativa - legível)
python3 scripts/preparacao/consolidar_nma.py <pasta> --format gro

# .dcd (GROMACS)
python3 scripts/preparacao/consolidar_nma.py <pasta> --format dcd
```

---

## 👀 Visualizar Animação {#visualizar}

Depois de consolidar, visualize os 20 frames em movimento!

### No CHIMERA (Recomendado)

```bash
# Abrir trajetória com topologia
chimera \
    screening_results/ctr3_Fluconazole/complexo_final.pdb \
    screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc

# Depois na interface:
# 1. MD Movie → Play
# 2. Observe 20 frames em sequência (canalabrindo/fechando)
# 3. Use slider para ir frame a frame
```

### No PyMOL

```bash
# Abrir arquivo
pymol screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc

# No console PyMOL:
python
open "screening_results/ctr3_Fluconazole/complexo_final.pdb"
load "screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc"
# Use Movie panel para animar
quit
```

### No GROMACS

```bash
# Converter para PDB individual
gmx trjconv \
    -s screening_results/ctr3_Fluconazole/complexo_final.pdb \
    -f screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc \
    -o frame_?.pdb
```

---

## 🎯 Docking Iterativo em NMA {#docking-nma}

Após gerar e consolidar NMA, execute **docking em cada frame** para ver como afinidade varia!

### Passo 1: Verificar Pré-requisitos

```bash
# Verificar Vina
which vina
conda install -c conda-forge autodock-vina

# Verificar OpenBabel
which obabel
conda install -c conda-forge openbabel
```

### Passo 2: Docking Manual (1 ligante)

```bash
cd /home/brilha/bioinformatica/codigos_mestres

# Executar para ligante específico
python3 scripts/docking/docking_nma_iterativo.py \
    screening_results/ctr3_Fluconazole

# Resultado:
# ✅ 20 arquivos resultado_docking_NMA_01.pdbqt até NMA_20.pdbqt
# ✅ docking_nma_summary.json com estatísticas
```

### Passo 3: Docking Automático (TODOS os ligantes)

```bash
cd /home/brilha/bioinformatica/codigos_mestres

# Script pronto - roda docking em todos
# Opção A: Sequencial (um por vez)
./docking_todos_nma.sh

# Opção B: Paralelo (todos simultaneamente - CPU intensivo!)
./docking_todos_nma.sh --parallel
```

### Passo 4: Ver Resultados

```bash
# Arquivo JSON com estatísticas
cat screening_results/ctr3_Fluconazole/docking_nma_summary.json | jq '.'

# Esperado:
# {
#   "statistics": {
#     "best_frame": 12,
#     "min_energy": -7.234,
#     "mean_energy": -6.142,
#     "max_energy": -4.891
#   }
# }
```

### Interpretação

```
best_frame: 12
  → Frame 12 tem MELHOR afinidade (mais negativo = melhor)

min_energy: -7.234 (melhor)
max_energy: -4.891 (pior)
  → Variação de 2.3 kcal/mol entre frames
  → Movimento do canal é SIGNIFICATIVO

Conclusão:
  → Conformação do frame 12 é ideal para este ligante
  → Pode ser mais promissor que estado original fechado
```

---

## 🆘 Troubleshooting {#troubleshooting}

### ❌ "Arquivo complexo_final.pdb não encontrado"

```bash
# Procurar arquivo
find . -name "complexo_final.pdb" -o -name "complexo_*.pdb"

# Se não achar:
# 1. Rode docking normal primeiro
# 2. Depois rode NMA
```

### ❌ "NMA não gerou arquivos"

```bash
# Verificar se ProDy está instalado
python3 -c "import prody; print(prody.__version__)"

# Se não:
conda install prody
# ou
pip install prody
```

### ❌ "Consolidação falhou - MDTraj não encontrado"

```bash
pip install mdtraj
```

### ❌ "Docking iterativo muito lento"

```bash
# Normal: ~1 min por frame × 20 = 20 minutos

# Se muito lento (>2 min/frame):
# 1. Verificar CPU: top ou htop
# 2. Reduzir exhaustiveness em config.txt:
#    De 8 para 4 (menos preciso, mais rápido)
```

### ❌ ".xtc não abre em CHIMERA"

```bash
# Abrir com topologia explícita
chimera complexo_final.pdb complexo_NMA_completo.xtc

# Ou usar .gro em vez de .xtc
python3 scripts/preparacao/consolidar_nma.py <pasta> --format gro
```

---

## 📋 Workflow Completo (Passo-a-passo)

### Opção 1: Via Master Script (Rápido)

```bash
cd /home/brilha/bioinformatica/codigos_mestres

# 1. Rodar master script
python3 virtual_screening_mestre.py config.yaml
   # Escolher alvo + ligantes
   # Escolher NMA quando pedir passos opcionais

# 2. Consolidar (automático no master)
# OU manual:
./consolidar_todos_nma.sh

# 3. Visualizar
chimera screening_results/ctr3_Fluconazole/complexo_final.pdb \
        screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc
# MD Movie → Play

# 4. Docking iterativo
./docking_todos_nma.sh

# 5. Analisar
cat screening_results/ctr3_*/docking_nma_summary.json | jq '.'
```

### Opção 2: Separadamente (Flexível)

```bash
cd /home/brilha/bioinformatica/codigos_mestres/screening_results/ctr3_Fluconazole

# 1. Gerar NMA
python3 ../../scripts/preparacao/aplicar_nma.py .

# 2. Verificar
ls -1 complexo_final_NMA_*.pdb | wc -l

# 3. Consolidar
python3 ../../scripts/preparacao/consolidar_nma.py . --format xtc

# 4. Visualizar
chimera complexo_final.pdb complexo_NMA_completo.xtc

# 5. Docking iterativo
python3 ../../scripts/docking/docking_nma_iterativo.py .

# 6. Resultado
cat docking_nma_summary.json | jq '.statistics'
```

---

## ✅ Checklist: NMA Completo

- [ ] **Geração NMA**
  - [ ] Arquivo `complexo_final.pdb` existe
  - [ ] 20 frames `complexo_final_NMA_*.pdb` gerados

- [ ] **Consolidação**
  - [ ] MDTraj instalado
  - [ ] Arquivo `.xtc` criado (0.12 MB ou similar)

- [ ] **Visualização**
  - [ ] Abre em CHIMERA com topologia
  - [ ] Animação funciona (MD Movie)

- [ ] **Docking Iterativo**
  - [ ] Vina + OpenBabel instalados
  - [ ] 20 PDBQT gerados
  - [ ] JSON com energias criado

- [ ] **Análise**
  - [ ] Melhor frame identificado
  - [ ] Energias variação compreendidas

---

## 📞 Resumo Rápido

| Tarefa | Comando | Tempo |
|--------|---------|-------|
| Gerar 20 frames NMA | `python3 scripts/preparacao/aplicar_nma.py .` | 5 min |
| Consolidar em .xtc | `python3 scripts/preparacao/consolidar_nma.py . --format xtc` | 1 min |
| Visualizar em CHIMERA | `chimera complexo_final.pdb complexo_NMA_completo.xtc` | Manual |
| Docking em 20 frames | `python3 scripts/docking/docking_nma_iterativo.py .` | 20 min |
| Tudo junto (automático) | `./consolidar_todos_nma.sh && ./docking_todos_nma.sh` | 25 min |

---

**⭐ LEMBRETE IMPORTANTE:**

Você pode rodar NMA em **qualquer momento**, com **qualquer ligante+proteína**, **não precisa ser durante o master script**!

Basta ter um arquivo `complexo_final.pdb` e rodar:
```bash
python3 scripts/preparacao/aplicar_nma.py <pasta>
```

Depois consolide e visualize!

---

_Documento criado: 28 de Janeiro de 2026_  
_Última atualização: Versão 2.0 - Completa e Simplificada_
