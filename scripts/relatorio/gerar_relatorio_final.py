import sys
import os
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, QED

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

def ler_energia_vina(pasta):
    caminho_log = os.path.join(pasta, "log.txt") # Ou log_docking.txt dependendo de como salvou
    if not os.path.exists(caminho_log):
        # Tenta achar qualquer .txt que pareça log
        try:
            caminho_log = [f for f in os.listdir(pasta) if "log" in f and f.endswith(".txt")][0]
            caminho_log = os.path.join(pasta, caminho_log)
        except:
            return "N/A (Log não encontrado)"
    
    with open(caminho_log, 'r') as f:
        for line in f:
            # Procura a linha da primeira pose (mode 1)
            if line.strip().startswith("1"):
                partes = line.split()
                if len(partes) >= 2:
                    return f"{partes[1]} kcal/mol"
    return "N/A"

def ler_interacoes_plip(pasta):
    # Procura o report.txt do PLIP
    arquivos = os.listdir(pasta)
    report_file = next((f for f in arquivos if "report.txt" in f), None)
    
    if not report_file:
        return "Relatório PLIP não encontrado."
        
    caminho = os.path.join(pasta, report_file)
    resumo = {}
    
    with open(caminho, 'r') as f:
        texto = f.read()
        # Conta ocorrências das palavras chave do PLIP
        resumo['Hydrophobic Interactions'] = texto.count('Hydrophobic Interaction')
        resumo['Hydrogen Bonds'] = texto.count('Hydrogen Bond')
        resumo['Pi-Stacking'] = texto.count('pi-Stacking')
        resumo['Salt Bridges'] = texto.count('Salt Bridge')
        
    txt_saida = ""
    for tipo, qtd in resumo.items():
        if qtd > 0:
            txt_saida += f"- {tipo}: {qtd}\n"
            
    if not txt_saida: return "Nenhuma interação detectada."
    return txt_saida

def analisar_quimica(pasta):
    # Procura o SDF
    arquivos = os.listdir(pasta)
    sdf_file = next((f for f in arquivos if f.endswith(".sdf")), None)
    
    if not sdf_file: return "SDF não encontrado."
    
    suppl = Chem.SDMolSupplier(os.path.join(pasta, sdf_file), sanitize=False)
    mol = next(suppl)
    if not mol: return "Erro ao ler molécula."
    try: Chem.SanitizeMol(mol)
    except: pass
    
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    qed = QED.qed(mol)
    
    lipinski_fail = 0
    if mw > 500: lipinski_fail += 1
    if logp > 5: lipinski_fail += 1
    # ... (outras regras simplificadas)
    
    status = "APROVADO" if lipinski_fail <= 1 else "ALERTA (Violações)"
    
    return f"""
    - Peso Molecular: {mw:.2f}
    - LogP: {logp:.2f}
    - QED Score: {qed:.3f}
    - Status Lipinski: {status}
    """

def gerar_markdown(pasta):
    """✅ CORRIGIDO: Gera HTML em vez de MD com CSS"""
    nome_projeto = os.path.basename(os.path.normpath(pasta))
    
    energia = ler_energia_vina(pasta)
    quimica = analisar_quimica(pasta)
    interacoes = ler_interacoes_plip(pasta)
    
    relatorio_md = f"""# 📄 Relatório Integrado de Bioinformática
## Projeto: {nome_projeto}
---

### 1. 🎯 Resultado do Docking (Vina)
**Afinidade de Ligação:** `{energia}`
> *Nota: Valores abaixo de -7.0 kcal/mol indicam forte interação.*

---

### 2. 💊 Propriedades Farmacocinéticas
{quimica}

---

### 3. 🔗 Perfil de Interação (PLIP)
Resumo das forças que mantêm o fármaco no alvo:
{interacoes}

---

### 4. 📂 Arquivos Gerados
Para visualizar, procure na pasta:
- **3D:** `*.pse` (Sessão PyMOL)
- **2D:** `*_structure.png` (Química)
- **Log:** `log.txt` (Dados brutos)

---
*Gerado automaticamente pelo Pipeline Bioinfo-Du.*
    """
    
    # ✅ NOVO: Gerar HTML com CSS
    html_content = ""
    if HAS_MARKDOWN:
        html_content = markdown.markdown(relatorio_md)
    else:
        # Fallback: HTML simples sem markdown
        html_content = f"<h1>📄 Relatório Integrado de Bioinformática</h1><h2>Projeto: {nome_projeto}</h2>" + relatorio_md.replace('\n', '<br>')
    
    html_saida = os.path.join(pasta, "relatorio_final.html")
    with open(html_saida, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Final - {nome_projeto}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h1 {{ font-size: 2em; }}
        h2 {{ font-size: 1.5em; }}
        h3 {{ font-size: 1.2em; }}
        code {{
            background: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #7f8c8d;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    {html_content}
    <div class="footer">
        <p>Gerado automaticamente pelo Pipeline Bioinfo-Du em {os.path.basename(pasta)}</p>
    </div>
</body>
</html>""")
    
    print(f"✅ Relatório gerado com sucesso: {html_saida}")
    print("📖 Abra este arquivo no seu navegador para visualizar.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 gerar_relatorio_final.py <pasta_projeto>")
    else:
        gerar_markdown(sys.argv[1])