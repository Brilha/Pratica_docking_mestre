# 🔧 TROUBLESHOOTING - Virtual Screening Master

## ❓ Problemas Comuns e Soluções

---

## 1. ModuleNotFoundError: No module named 'yaml'

**Problema:**
```
ModuleNotFoundError: No module named 'yaml'
```

**Solução:**
```bash
pip install pyyaml
```

Ou se estiver usando conda:
```bash
conda install pyyaml
```

---

## 2. FileNotFoundError: 'config.yaml' not found

**Problema:**
```
FileNotFoundError: Arquivo de configuração não encontrado: config.yaml
```

**Solução:**
Certifique-se de que está no diretório correto:
```bash
cd /home/brilha/bioinformatica/codigos_mestres
ls config.yaml  # Verificar se existe
python3 virtual_screening_mestre.py config.yaml
```

Se o arquivo não existir, ele foi criado durante a refatoração. Verifique se todos os arquivos foram criados:
```bash
ls -la *.yaml *.py
```

---

## 3. Ferramenta não encontrada (vina, obabel, plip)

**Problema:**
```
❌ Ferramenta não encontrada: vina
```

**Solução:**
Instale as ferramentas requeridas:

### AutoDock Vina
```bash
# Ubuntu/Debian
sudo apt-get install autodock-vina

# Ou download manual
wget https://vina.scripps.edu/download/autodock_vina_linux_x86.tar.gz
tar xzf autodock_vina_linux_x86.tar.gz
sudo mv autodock_vina_1_1_2_linux_x86/bin/vina /usr/local/bin/
```

### OpenBabel
```bash
# Ubuntu/Debian
sudo apt-get install openbabel

# macOS
brew install open-babel
```

### PLIP
```bash
pip install plip
```

Verificar instalação:
```bash
which vina
which obabel
which plip
```

---

## 4. Timeout na execução de um passo

**Problema:**
```
❌ Timeout (600s) ao executar: python3 preparar_arquivosuniversal.py ...
```

**Solução:**
Aumentar timeout em `config.yaml`:
```yaml
docking:
  timeout_seconds: 1200  # Aumentar de 600 para 1200
```

Ou executar o script manualmente para identificar o problema:
```bash
cd screening_results/mapk_Iprodione
python3 ../../preparar_arquivosuniversal.py .
```

---

## 5. Arquivo de saída não criado

**Problema:**
```
❌ [preparacao] Arquivos de saída não foram criados: 
   ['screening_results/mapk_Iprodione/receptor.pdbqt']
```

**Solução:**
1. Verificar se o script foi executado:
   ```bash
   ls -la screening_results/mapk_Iprodione/
   ```

2. Verificar logs do script:
   ```bash
   cat logs/screening_*.log | grep -A 10 "preparacao"
   ```

3. Executar script manualmente para debug:
   ```bash
   cd screening_results/mapk_Iprodione
   python3 ../../preparar_arquivosuniversal.py .
   ```

---

## 6. Arquivo PDB não encontrado no RCSB

**Problema:**
```
❌ Falha ao baixar PDB: ...
```

**Solução:**
1. Verificar se o código PDB está correto:
   ```bash
   curl -s "https://www.rcsb.org/search/pdb_search/mapk.json" | head
   ```

2. Usar arquivo local se disponível:
   - Coloque `mapk.pdb` no diretório de trabalho
   - Script detectará automaticamente

3. Verificar conectividade internet:
   ```bash
   ping www.rcsb.org
   ```

---

## 7. Vina falhando durante docking

**Problema:**
```
❌ [docking] Execução falhou
```

**Solução:**
1. Verificar config.txt:
   ```bash
   cat screening_results/mapk_Iprodione/config.txt
   ```

2. Verificar log do Vina:
   ```bash
   cat screening_results/mapk_Iprodione/log_docking.txt
   ```

3. Executar Vina manualmente:
   ```bash
   cd screening_results/mapk_Iprodione
   vina --config config.txt --out resultado_docking.pdbqt
   ```

---

## 8. Memória insuficiente durante docking

**Problema:**
```
MemoryError ou processo killed
```

**Solução:**
1. Reduzir tamanho do grid em `config.yaml`:
   ```yaml
   docking:
     grid_size: 15  # Reduzir de 20
     cpu_count: 2   # Reduzir CPUs
   ```

2. Monitorar uso de memória:
   ```bash
   watch -n 1 free -h
   ```

3. Fechar aplicações desnecessárias

---

## 9. Passo sendo pulado quando não deveria

**Problema:**
```
[preparacao] ⏭️  Pulando: Arquivos de entrada ausentes
```

**Solução:**
Verificar se arquivos de entrada existem:
```bash
ls -la screening_results/mapk_Iprodione/mapk.pdb
ls -la screening_results/mapk_Iprodione/Iprodione.sdf
```

Se não existem, executar `preparar_pasta_alvo()` novamente ou baixar manualmente.

---

## 10. Erro de permissão ao criar diretórios

**Problema:**
```
PermissionError: [Errno 13] Permission denied
```

**Solução:**
```bash
# Verificar permissões
ls -la /home/brilha/bioinformatica/codigos_mestres/

# Se necessário, ajustar
chmod 755 /home/brilha/bioinformatica/codigos_mestres/
chmod 755 screening_results/ -R

# Executar com sudo se necessário (não recomendado)
# sudo python3 virtual_screening_mestre.py config.yaml
```

---

## 11. Pipeline interrompido - como resumir?

**Problema:**
Execução foi cancelada no meio (`Ctrl+C`), precisa resumir.

**Solução:**
A refatoração suporta checkpoints! (Implementação futura)

Por enquanto, deletar pasta incompleta e reexecutar:
```bash
rm -rf screening_results/mapk_Iprodione/
python3 virtual_screening_mestre.py config.yaml
```

---

## 12. Logs não estão sendo criados

**Problema:**
Diretório `logs/` vazio ou não existe.

**Solução:**
```bash
# Verificar se diretório foi criado
ls -la logs/

# Se não existe, criá-lo manualmente
mkdir -p logs/

# Verificar permissões
touch logs/test.txt
rm logs/test.txt
```

---

## 13. Config.yaml inválido

**Problema:**
```
yaml.YAMLError: mapping values are not allowed here
```

**Solução:**
YAML é sensível a indentação. Verificar:
```bash
python3 -m yaml config.yaml  # Validar sintaxe
```

ou usar um validador online:
https://www.yamllint.com/

Problemas comuns:
- Espaços vs tabs (sempre use espaços)
- Falta de ':' após chaves
- Indentação inconsistente

---

## 14. Performance lenta

**Problema:**
Execução está demorando muito.

**Solução:**
1. Aumentar CPUs em `config.yaml`:
   ```yaml
   docking:
     cpu_count: 8  # Aumentar de 4
   ```

2. Reduzir número de combinações target-drug:
   ```yaml
   targets: [mapk]  # Apenas um alvo
   drugs: [Iprodione]  # Apenas uma droga
   ```

3. Monitorar sistema:
   ```bash
   htop  # Monitorar CPU/Memória
   ```

---

## 15. ImportError em módulos customizados

**Problema:**
```
ImportError: cannot import name 'X' from 'utils'
```

**Solução:**
Verificar que todos os arquivos estão no mesmo diretório:
```bash
ls -la *.py
```

Se falta algum arquivo, recriar:
```bash
git checkout utils.py pipeline_step.py
```

Ou copiar de exemplo online.

---

## 🆘 Debug Avançado

### Ativar modo DEBUG
```bash
# Editar config.yaml
logging:
  level: DEBUG  # Era INFO
```

Logs com debug incluem mais informações:
```bash
tail -100 logs/screening_*.log
```

### Executar passos individualmente
```bash
cd screening_results/mapk_Iprodione
python3 ../../preparar_arquivosuniversal.py .
python3 ../../definir_gridbox.py .
python3 ../../analise_quimica_completa.py Iprodione.sdf
```

### Inspeccionar estado
```bash
# Ver arquivos criados
find screening_results/mapk_Iprodione/ -type f | sort

# Ver checkpoint (se existir)
cat screening_results/mapk_Iprodione/.checkpoint.json
```

---

## 📞 Contato / Mais Informações

Se problema persiste:
1. Verificar [README_REFACTORING.md](README_REFACTORING.md)
2. Consultar [EXEMPLOS.py](EXEMPLOS.py)
3. Verificar logs em `./logs/screening_*.log`
4. Abrir issue no repositório

---

**Última Atualização:** 27/01/2026
