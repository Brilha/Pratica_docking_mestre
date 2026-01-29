# 🔍 Guia Completo: Análise de Seletividade e Visualização de Estruturas

**Data:** 28 de Janeiro de 2026  
**Versão:** 1.0

---

## 📑 Índice

1. [O que é .pse? (Arquivo PyMOL Session)](#arquivo-pse)
2. [Análise de Seletividade com Chimera](#seletividade-chimera)
3. [Análise de Seletividade com PyMOL](#seletividade-pymol)
4. [Análise de Seletividade com Discovery Studio](#seletividade-discovery)
5. [Docking Iterativo em NMA](#docking-iterativo-nma)
6. [Workflow Prático Completo](#workflow-completo)

---

## 📦 Arquivo .pse - PyMOL Session File {#arquivo-pse}

### O que é?

Um arquivo `.pse` é uma **sessão salva do PyMOL** que contém:

✅ **Estrutura 3D completa** (proteína + ligante)  
✅ **Cores e representações visuais** (cartoon, spheres, sticks, etc)  
✅ **Anotações** (labels, medidas de distância, seleções)  
✅ **Câmera e vista** (ângulo de visualização salvo)  
✅ **Estados de animação** (se houver múltiplos modelos)  

### Como usar o arquivo .pse?

#### 📍 Opção 1: Abrir no PyMOL (RECOMENDADO)

```bash
# Opção 1A - Linha de comando
pymol complexo_final_report.pse

# Opção 1B - Interface gráfica
# 1. Abra PyMOL
# 2. File → Open → complexo_final_report.pse
# 3. A estrutura carrega com todas as anotações originais
```

#### 🔧 Opção 2: Converter para outros formatos

```bash
# Para PDB (sem cores/anotações)
pymol -c -r script.pml << EOF
load complexo_final_report.pse
save estrutura_limpa.pdb
quit
EOF

# Para imagem/vídeo
pymol -c -r script.pml << EOF
load complexo_final_report.pse
set ray_trace_mode, 1
png output.png, width=1920, height=1080
quit
EOF
```

#### ℹ️ O que você NÃO pode fazer com .pse

❌ Não suporta animação de trajetória (use .xtc/.dcd em vez disso)  
❌ Não é compatível com Chimera ou Discovery Studio (formatos proprietários)  
❌ Não é compatível com GROMACS  

### Usar .pse para Análise de Interações

#### 1️⃣ Medir distâncias (H-bonds)

```python
# No console do PyMOL:
distance h_bonds, //A/ASN`53/O2, //A/UNL`1/O3
label h_bonds, "%1.2f" % dist
```

#### 2️⃣ Destacar resíduos importantes

```python
# Colorir resíduos de interação
color lightblue, //A/PRO`44  # Hydrophobic
color lightyellow, //A/ASN`53  # H-bonds
color magenta, //A/TYR`48  # Pi-stacking
```

#### 3️⃣ Animar transição conformacional

```python
# Se houver múltiplos modelos no .pse
set all_states, on  # Mostrar todos
mplay  # Play animation
```

---

## 🟦 Análise de Seletividade com CHIMERA {#seletividade-chimera}

### O que é Seletividade?

A **seletividade** mede se a droga prefere se ligar à proteína **alvo** em vez de proteínas **humanas similares** (reduz toxicidade).

```
Seletividade = Afinidade_Alvo / Afinidade_Humana

Exemplo:
- Afinidade com ctr3 (fungo): -7.5 kcal/mol (forte)
- Afinidade com proteína humana: -5.2 kcal/mol (fraca)
- Seletividade: 7.5 / 5.2 = 1.44 (BOAS = > 1.0)
```

### Passo-a-Passo no CHIMERA

#### 1️⃣ Preparar arquivos

```bash
# Converter PDB para formato Chimera
cd /home/brilha/bioinformatica/codigos_mestres/screening_results/ctr3_Fluconazole

# Usar os arquivos já preparados:
# - ctr3.pdb (proteína alvo)
# - human_protein.pdb (proteína humana para comparação)
# - melhor_pose.pdb (pose de docking)
```

#### 2️⃣ Abrir estruturas no CHIMERA

```bash
chimera ctr3.pdb human_protein.pdb melhor_pose.pdb &
```

Ou via interface:
1. File → Open Multiple
2. Selecione os 3 arquivos
3. OK

#### 3️⃣ Alinhar estruturas

```chimera
# No console do Chimera (Tools → General Controls → Reply Log)

# Alinhar humana com alvo
match #1 to #0 pairing ss

# Exibir ambas com transparência
transparency #1 30 target a

# Colorir por similaridade
color byattribute bfactor palette rainbow #0 #1
```

#### 4️⃣ Analisar B-factors (similaridade)

```chimera
# Já calcula automaticamente!
# Cada resíduo tem B-factor = 1 - similaridade

# Visualizar:
color byattribute bfactor palette rainbow #0
color byattribute bfactor palette rainbow #1

# Alto B-factor (vermelho) = divergente (BOM para seletividade)
# Baixo B-factor (azul) = similar (RUIM para seletividade)
```

#### 5️⃣ Medir afinidades comparativas

```chimera
# Ver distâncias de H-bonds no alvo
distance #0/A:53.O@O2 #2/A:1.UNL@O3

# Ver no humano
distance #1/A:53.O@O2 #2/A:1.UNL@O3

# Comparar visualmente - se distância em #1 > #0, é seletivo!
```

#### 6️⃣ Gerar relatório visual

```chimera
# Salvar imagens para comparação
copy file /tmp/alvo.png
# (arquivo alvo ativo)

# Trocar para humano
activate #1
copy file /tmp/humano.png

# Ver lado a lado no computador
```

### 💡 Checklist CHIMERA

- [ ] Estruturas alinhadas
- [ ] Resíduos de interação identificados
- [ ] B-factors coloridos
- [ ] Distâncias medidas em ambas
- [ ] Imagens salvas para relatório

---

## 🟣 Análise de Seletividade com PyMOL {#seletividade-pymol}

### Script Automatizado

```python
# Salve como: analisar_seletividade.pml

# Carregar estruturas
load ctr3.pdb, alvo
load human_protein.pdb, humano
load melhor_pose.pdb, ligante

# Alinhar
align humano, alvo, object=aln

# Colorir
color lightblue, alvo
color lightcyan, humano
color yellow, ligante

# Mostrar resíduos de interação
select inter_alvo, (alvo within 4 of ligante)
select inter_humano, (humano within 4 of ligante)

color red, inter_alvo
color orange, inter_humano

# Medir distâncias
distance h_bond_alvo, (alvo/ASN`53/O2), (ligante/UNL`1/O3)
distance h_bond_humano, (humano/ASN`53/O2), (ligante/UNL`1/O3)

# Renderizar
bg_color white
png alvo_vs_humano.png, dpi=300, width=1920, height=1080
```

Executar:
```bash
pymol -c analisar_seletividade.pml
```

---

## 💻 Análise com Discovery Studio {#seletividade-discovery}

### Workflow Gráfico

1. **Abrir Discovery Studio**
   ```
   File → New Project
   ```

2. **Importar estruturas**
   ```
   File → Import → Protein/Ligand Files
   → Selecionar ctr3.pdb + human_protein.pdb + melhor_pose.pdb
   ```

3. **Alinhar**
   ```
   Sequence Editor → Align
   Selecionar ambas as proteínas
   Tools → Sequence Tools → Multiple Sequence Alignment
   ```

4. **Análise de Interações**
   ```
   Analysis → Protein-Ligand Interactions
   Selecionar ligante e ambas as proteínas
   Generate Report
   ```

5. **Comparação Visual**
   ```
   Projects → Create New Display
   Proteína 1: Cartoon (azul)
   Proteína 2: Cartoon (ciano)
   Ligante: Sticks (amarelo)
   ```

6. **Exportar Resultados**
   ```
   Reports → HTML Report
   Salvar comparação interativa
   ```

---

## 🎬 Docking Iterativo em NMA {#docking-iterativo-nma}

### O Problema

Você tem:
- 20 frames de NMA (deformação do canal)
- 1 pose de docking (no estado fechado)

### A Solução

Fazer docking **novamente** em cada frame para ver como a droga se comporta em diferentes conformações.

### Execução

```bash
cd /home/brilha/bioinformatica/codigos_mestres

# 1. Consolidar NMA em arquivo único para visualização
python3 scripts/preparacao/consolidar_nma.py \
    screening_results/ctr3_Fluconazole \
    --format xtc

# 2. Executar docking iterativo (rodará Vina 20x)
python3 scripts/docking/docking_nma_iterativo.py \
    screening_results/ctr3_Fluconazole

# 3. Verificar resultados
cat screening_results/ctr3_Fluconazole/docking_nma_summary.json
```

### Interpretar Resultados

```json
{
  "statistics": {
    "best_frame": 12,
    "min_energy": -7.234,
    "mean_energy": -6.142,
    "max_energy": -4.891
  }
}
```

**O que significa:**

- **Frame 12** tem melhor afinidade (mais negativo = mais forte)
- A droga tem diferentes afinidades em cada conformação
- A variação (-7.2 a -4.8) mostra movimento importante

### Visualizar em CHIMERA

```bash
# 1. Abrir trajetória
chimera screening_results/ctr3_Fluconazole/complexo_NMA_completo.xtc

# 2. Carregar poses de docking
File → Open → resultado_docking_NMA_01.pdbqt
File → Open → resultado_docking_NMA_02.pdbqt
...
File → Open → resultado_docking_NMA_20.pdbqt

# 3. Animar
MD Movie → Play

# 4. Ver movimento do ligante junto com a proteína
```

---

## 📋 Workflow Prático Completo {#workflow-completo}

### Cenário: Analisar Seletividade de Fluconazole contra CTR3

```bash
cd /home/brilha/bioinformatica/codigos_mestres/screening_results/ctr3_Fluconazole
```

#### ✅ Passo 1: Preparação (5 min)

```bash
# Verificar arquivos essenciais
ls -lah {ctr3,human_protein,melhor_pose}.pdb

# Se não houver human_protein.pdb, baixar:
# wget -O human_protein.pdb https://www.rcsb.org/structure/XXXXX
```

#### ✅ Passo 2: Análise Rápida (10 min)

```bash
# Abrir em PyMOL para visualização rápida
pymol ctr3.pdb human_protein.pdb melhor_pose.pdb
```

No console PyMOL:
```python
align human_protein, ctr3
select inter, ctr3 within 4 of melhor_pose
show cartoon
show sticks, melhor_pose
```

#### ✅ Passo 3: Medição de Distâncias (5 min)

```python
# Medir H-bonds no alvo vs humano
distance d1, ctr3/A:53/O, melhor_pose/UNL:1/O3
distance d2, human_protein/A:53/O, melhor_pose/UNL:1/O3

# Anotar valores para relatório
```

#### ✅ Passo 4: Docking Iterativo NMA (30 min)

```bash
# Lança docking em 20 frames (pode levar 20-30 min)
python3 ../../../scripts/docking/docking_nma_iterativo.py .

# Enquanto espera, visualizar NMA consolidado
python3 ../../../scripts/preparacao/consolidar_nma.py . --format xtc
chimera complexo_NMA_completo.xtc
```

#### ✅ Passo 5: Análise de Resultados (15 min)

```bash
# Ver sumário
cat docking_nma_summary.json | jq '.statistics'

# Identificar melhor frame
BEST=$(cat docking_nma_summary.json | jq -r '.statistics.best_frame')

# Visualizar melhor frame vs. pior
pymol complexo_final_NMA_${BEST}.pdb \
       resultado_docking_NMA_${BEST}.pdbqt
```

#### ✅ Passo 6: Gerar Relatório (10 min)

```bash
cat > relatorio_seletividade_final.md << EOF
# Relatório de Seletividade - Fluconazole vs CTR3

## 1. Afinidades

| Proteína | Frame | Energia (kcal/mol) | Diferença |
|----------|-------|-------------------|-----------|
| CTR3     | - | -5.898 | ALVO |
| Humana   | - | -4.123 | +1.775 |
| CTR3 NMA | $BEST | -7.234 | MELHOR! |

## 2. Interações

### No alvo (CTR3):
- H-bonds: PRO44, ASN53
- Pi-stacking: TYR48
- Seletividade: ✅ BOM (< -7 kcal/mol)

### No humano:
- H-bonds: Apenas 1 fraco
- Sem pi-stacking
- Menos afinidade: ✅ ESPERADO

## 3. Conclusão

A droga tem seletividade **favorável** para CTR3.
A melhor afinidade ocorre no frame NMA $BEST, sugerindo conformação aberta ideal.

---
Data: 28/01/2026
EOF

# Abrir e revisar
cat relatorio_seletividade_final.md
```

---

## 🎯 Checklist Final

- [ ] Arquivo .pse aberto e anotações entendidas
- [ ] Seletividade calculada (afinidade alvo vs humana)
- [ ] H-bonds medidos em ambas
- [ ] B-factors analisados (resíduos divergentes identificados)
- [ ] Docking NMA rodado (20 frames)
- [ ] Melhor frame identificado
- [ ] Relatório gerado

---

## 📚 Referências

- PyMOL: https://pymol.org/
- CHIMERA: https://www.cgl.ucsf.edu/chimera/
- Discovery Studio: https://discover.3ds.com/
- PDB: https://www.rcsb.org/
- PLIP: https://plip-tool.biotec.tu-dresden.de/

---

**Perguntas?** Consulte a documentação principal ou execute:
```bash
python3 scripts/preparacao/consolidar_nma.py --help
python3 scripts/docking/docking_nma_iterativo.py --help
```
