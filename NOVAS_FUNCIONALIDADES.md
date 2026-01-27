# ✅ NOVAS FUNCIONALIDADES IMPLEMENTADAS

## 1. 🧬 Análise de Seletividade com Proteína Humana

### Descrição
A seletividade é crítica para evitar toxicidade de fármacos. O sistema agora permite:
- Comparar sua proteína alvo com sua proteína humana equivalente
- Usar BLAST para identificar regiões idênticas (PERIGOSAS - alto risco de toxicidade)
- Colorir o PDB por B-factor para visualizar similaridade com humana

### Como Usar
1. Coloque suas proteínas humanas de referência em `templates/proteinas_humanas/`
   - Exemplo: `templates/proteinas_humanas/human_mapk.pdb`

2. Configure em `config.yaml`:
   ```yaml
   human_proteins:
     - human_mapk
     - human_pdrk
   ```

3. Na execução, você será perguntado se deseja ativar análise de seletividade
4. Escolha qual proteína humana usar para comparação

### Scripts Utilizados
- `scripts/utils/check_seletividadeuniversal.py` - BLAST vs Homo sapiens
- `scripts/utils/cor_pdb_seletividade.py` - Colorir por B-factor no Chimera

### Visualização
No Chimera, abra o arquivo colorido e use:
```
Tools → Depiction → Render by Attribute (residues → average bfactor)
```

---

## 2. 🔬 Detecção Automática 2D→3D

### Descrição
SDFs do PubChem frequentemente vêm em conformação 2D. O sistema agora:
- Detecta automaticamente se SDF está em 2D (sem variação em eixo Z)
- Converte para 3D com OpenBabel (algoritmo `--gen3d best`)
- Minimiza energia com MMFF94 (500 iterações)

### Como Funciona
1. Durante a preparação (`preparacao` step), o script verifica dimensionalidade
2. Se 2D detectado:
   - Gera coordenadas 3D
   - Minimiza energia
   - Usa arquivo convertido automaticamente
3. Se 3D: pula a conversão

### Saída
Arquivos criados:
- Original: `Iprodione.sdf` (2D)
- Convertido: `Iprodione_3D_minimizado.sdf` (3D otimizado)

---

## 3. 📁 Estrutura de Proteínas Humanas

### Novo Diretório
```
templates/
├── proteins/              # Proteínas alvo
│   ├── mapk.pdb
│   ├── pdrk.pdb
│   └── ...
├── proteinas_humanas/    # ✅ NOVO: Referências humanas
│   ├── human_mapk.pdb
│   ├── human_pdrk.pdb
│   └── ...
└── drugs/
    ├── Iprodione.sdf
    ├── Fludioxonil.sdf
    └── ...
```

### Como Configurar
1. Baixe PDBs de proteínas humanas equivalentes
   - Use NCBI PDB ou PDBe
   - Recomendado: versões cristalográficas de alta resolução

2. Coloque em `templates/proteinas_humanas/`

3. Configure em `config.yaml`

---

## 4. 🎯 Pipeline Atualizado

### Novo Fluxo de Execução

```
┌─ Seleção de Targets/Drugs
├─ Pergunta: Ativar Seletividade? (com proteína humana)
├─ Pergunta: Scripts Opcionais?
└─ Pipeline:
   ├─ preparacao       (detecção 2D→3D automática)
   ├─ gridbox
   ├─ grid_cego
   ├─ docking
   ├─ quimica
   ├─ plip
   ├─ prolif
   ├─ relatorio
   ├─ [opcional] refinar_grid
   ├─ [opcional] seletividade_humana (novo!)
   ├─ [opcional] colorir_seletividade (novo!)
   └─ [opcional] ... outros scripts opcionais
```

### Novos Scripts Opcionais
- `seletividade_humana`: Compara via BLAST
- `colorir_seletividade`: Colore por B-factor

---

## 5. 🚀 Como Usar as Novas Funcionalidades

### Exemplo Completo
```bash
python3 virtual_screening_mestre.py config.yaml
```

**Prompts que aparecerão:**

1. **Seleção de Targets**
   ```
   📋 ALVOS PROTEICOS DISPONÍVEIS:
     1. mapk
     2. pdrk
   → 1  (ou "1,2" para ambos)
   ```

2. **Seleção de Drugs**
   ```
   💊 FÁRMACOS DISPONÍVEIS:
     1. Iprodione
     2. Fludioxonil
   → 1
   ```

3. **Seletividade (NOVO)**
   ```
   🧬 ANÁLISE DE SELETIVIDADE (TOXICIDADE)
   
   🧬 PROTEÍNAS HUMANAS DISPONÍVEIS:
     1. human_mapk
     2. human_pdrk
   → 1  (ou "não" para desativar)
   ```

4. **Scripts Opcionais**
   ```
   📋 SCRIPTS OPCIONAIS DISPONÍVEIS
   1. [ADVANCED] refinar_grid
   2. [ANALYSIS] seletividade
   ...
   → 1,3,5 (ou "nenhum")
   ```

---

## 6. ⚙️ Configuração em config.yaml

```yaml
# Proteínas humanas (novas)
human_proteins:
  - human_mapk_reference
  # - human_pdrk_reference

# Scripts opcionais novos
optional_steps:
  - name: "seletividade_humana"
    script: "check_seletividadeuniversal.py"
    description: "Compara com proteína humana via BLAST"
    category: "selectivity"
  
  - name: "colorir_seletividade"
    script: "cor_pdb_seletividade.py"
    description: "Colore PDB por B-factor (similaridade humana)"
    category: "selectivity"
```

---

## 7. 🔍 Detalhes Técnicos

### Detecção 2D vs 3D
- **2D**: Coordenadas Z praticamente zero (< 0.01 Å de range)
- **3D**: Variação significativa em Z
- Script: `scripts/preparacao/detectar_e_converter_2d_3d.py`

### Minimização de Energia
- **Método**: MMFF94 (Merck Molecular Force Field)
- **Iterações**: 500 passos
- **Ferramenta**: OpenBabel `--minimize`

### BLAST para Seletividade
- **Banco**: SwissProt
- **Organismo**: Homo sapiens
- **E-value**: 10.0 (permissivo, encontra ortólogos)
- **Saída**: Score de identidade por resíduo (0-100)

---

## 8. 📊 Comparação: Antes vs Depois

| Funcionalidade | Antes | Depois |
|---|---|---|
| Seleção Target/Drug | Automática (todos) | ✅ Menu interativo |
| Detecção 2D→3D | Manual | ✅ Automática |
| Seletividade Humana | Não existia | ✅ Menu + BLAST + coloração |
| Proteínas Humanas | Não suportadas | ✅ Subpasta templates |
| Scripts Opcionais | 6 | ✅ 8 (+ 2 novos) |

---

## 9. ⚠️ Requisitos

### Já Instalado
- RDKit (para detecção 2D)
- OpenBabel (para conversão 3D)
- BioPython (para BLAST)
- NCBI BLAST (para seletividade)

### Verificar
```bash
which obabel
which blastall
python3 -c "from rdkit import Chem; print('RDKit OK')"
```

---

## 10. 💡 Dicas de Uso

### Para Farmacêuticos
1. Sempre ative seletividade se tiver proteína humana
2. Revise PDBs coloridos no Chimera
3. Regiões em vermelho = ALTO RISCO de toxicidade

### Para Modeladores
1. Certifique-se que SDF do PubChem está em 3D
2. Se suspeitar de 2D, o sistema detecta automaticamente
3. Resultado: arquivo `*_3D_minimizado.sdf` otimizado

### Para Pesquisadores
1. Use para triagem rápida de múltiplos ligantes
2. Combine seletividade + docking para priorizar
3. Exporte dados para análise externa

---

## ✅ Checklist de Implementação

- ✅ Criada pasta `templates/proteinas_humanas/`
- ✅ Detecção 2D→3D automatizada em `preparar_arquivosuniversal.py`
- ✅ Menu interativo de proteína humana em `virtual_screening_mestre.py`
- ✅ Novo script `detectar_e_converter_2d_3d.py`
- ✅ Funções `descobrir_proteinas_humanas()` e `mostrar_opcoes_seletividade()`
- ✅ Integração no pipeline com proteína humana no context
- ✅ Config.yaml atualizado com `human_proteins` e scripts opcionais novos
- ✅ Toda sintaxe validada

---

## 🚀 Próximos Passos Sugeridos

1. Adicionar proteínas humanas em `templates/proteinas_humanas/`
2. Testar pipeline completo com seletividade
3. Revisar resultados de BLAST no Chimera
4. Documentar proteínas humanas usadas em cada projeto

