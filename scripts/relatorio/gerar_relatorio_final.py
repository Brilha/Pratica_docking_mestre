#!/usr/bin/env python3
"""
Gerar Relatório Final Simples
VERSÃO SIMPLIFICADA: HTML direto, sem markdown, simples e funcional
"""

import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, QED
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False


def ler_energia_vina(pasta: Path) -> str:
    """Lê energia de ligação do log de docking do Vina"""
    log_files = list(pasta.glob('log*.txt'))
    
    if not log_files:
        return "N/A"
    
    try:
        with open(log_files[0], 'r') as f:
            for line in f:
                if line.strip().startswith("1 "):
                    partes = line.split()
                    if len(partes) >= 2:
                        return f"{partes[1]} kcal/mol"
    except:
        pass
    
    return "N/A"


def ler_interacoes_plip(pasta: Path) -> str:
    """Lê resumo de interações do relatório PLIP"""
    report_files = list(pasta.glob('*report*.txt'))
    
    if not report_files:
        return "Nenhum relatório PLIP encontrado."
    
    try:
        with open(report_files[0], 'r') as f:
            texto = f.read()
            resumo = {
                'Hydrophobic Interactions': texto.count('Hydrophobic Interaction'),
                'Hydrogen Bonds': texto.count('Hydrogen Bond'),
                'Pi-Stacking': texto.count('pi-Stacking'),
                'Salt Bridges': texto.count('Salt Bridge'),
            }
    except:
        return "Erro ao ler relatório PLIP."
    
    linhas = []
    for tipo, qtd in resumo.items():
        if qtd > 0:
            linhas.append(f"<li>{tipo}: <strong>{qtd}</strong></li>")
    
    if not linhas:
        return "<p>Nenhuma interação detectada.</p>"
    
    return "<ul>" + "".join(linhas) + "</ul>"


def avaliar_drug_likeness(mol) -> tuple:
    """
    Avalia se a molécula segue a Regra de Lipinski
    Retorna: (está_ok, mensagem)
    
    Regra de Lipinski para drug-likeness:
    - MW ≤ 500 Da
    - LogP ≤ 5
    - H-Doadores ≤ 5
    - H-Aceitadores ≤ 10
    - Ligações rotáveis ≤ 10 (algumas permitem até 12)
    """
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    h_donors = Descriptors.NumHDonors(mol)
    h_acceptors = Descriptors.NumHAcceptors(mol)
    rotatable = Descriptors.NumRotatableBonds(mol)
    
    violations = 0
    detalhes = []
    
    # Verificar cada critério
    if mw > 500:
        violations += 1
        detalhes.append(f"MW: {mw:.2f} > 500 ❌")
    else:
        detalhes.append(f"MW: {mw:.2f} ≤ 500 ✅")
    
    if logp > 5:
        violations += 1
        detalhes.append(f"LogP: {logp:.2f} > 5 ❌")
    else:
        detalhes.append(f"LogP: {logp:.2f} ≤ 5 ✅")
    
    if h_donors > 5:
        violations += 1
        detalhes.append(f"H-Doadores: {h_donors} > 5 ❌")
    else:
        detalhes.append(f"H-Doadores: {h_donors} ≤ 5 ✅")
    
    if h_acceptors > 10:
        violations += 1
        detalhes.append(f"H-Aceitadores: {h_acceptors} > 10 ❌")
    else:
        detalhes.append(f"H-Aceitadores: {h_acceptors} ≤ 10 ✅")
    
    if rotatable > 10:
        violations += 1
        detalhes.append(f"Rotáveis: {rotatable} > 10 ⚠️")
    else:
        detalhes.append(f"Rotáveis: {rotatable} ≤ 10 ✅")
    
    # QED Score (0-1, quanto maior melhor)
    try:
        qed = QED.qed(mol)
    except:
        qed = None
    
    if violations == 0:
        status = "✅ EXCELENTE"
        classe = "Fármaco promissor - Segue a Regra de Lipinski"
    elif violations == 1:
        status = "⚠️ BOM"
        classe = "Bom fármaco com 1 violação menor"
    elif violations <= 2:
        status = "⚠️ ACEITÁVEL"
        classe = "Potencial fármaco com algumas limitações"
    else:
        status = "❌ POBRE"
        classe = "Improvável de ser um bom fármaco oral"
    
    return {
        'status': status,
        'classe': classe,
        'violations': violations,
        'detalhes': detalhes,
        'qed': qed,
        'mw': mw,
        'logp': logp,
        'h_donors': h_donors,
        'h_acceptors': h_acceptors,
        'rotatable': rotatable
    }


def ler_propriedades_quimicas(pasta: Path) -> tuple:
    """Lê propriedades químicas da droga e retorna (html_tabela, html_analise)"""
    try:
        sdf_files = list(pasta.glob('*.sdf'))
        
        if not sdf_files or not HAS_RDKIT:
            return "", ""
        
        with open(sdf_files[0], 'r') as f:
            mol_block = f.read()
        
        mol = Chem.MolFromMolBlock(mol_block)
        if mol is None:
            return "", ""
        
        # Avaliar drug-likeness
        analise = avaliar_drug_likeness(mol)
        
        # Formatar QED
        qed_str = f"{analise['qed']:.3f}" if analise['qed'] else 'N/A'
        
        # Tabela de propriedades
        tabela = f"""        <tr>
            <td>Peso Molecular</td>
            <td>{analise['mw']:.2f} g/mol</td>
        </tr>
        <tr>
            <td>LogP (Hidrofobicidade)</td>
            <td>{analise['logp']:.2f}</td>
        </tr>
        <tr>
            <td>H-Doadores</td>
            <td>{analise['h_donors']}</td>
        </tr>
        <tr>
            <td>H-Aceitadores</td>
            <td>{analise['h_acceptors']}</td>
        </tr>
        <tr>
            <td>Ligações Rotáveis</td>
            <td>{analise['rotatable']}</td>
        </tr>
        <tr>
            <td>QED Score</td>
            <td>{qed_str}</td>
        </tr>"""
        
        # HTML da análise drug-likeness
        detalhes_html = "<ul>" + "".join([
            f"<li>{detalhe}</li>" for detalhe in analise['detalhes']
        ]) + "</ul>"
        
        analise_html = f"""
        <div style="background: #f0f8ff; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; border-radius: 3px;">
            <h3 style="margin-top: 0; color: #2c3e50;">{analise['status']}</h3>
            <p><strong>Avaliação:</strong> {analise['classe']}</p>
            <p><strong>Violações de Lipinski:</strong> {analise['violations']}/5</p>
            <p><strong>Critérios:</strong></p>
            {detalhes_html}
            <p style="font-size: 0.9em; color: #666; margin-top: 10px;">
                <em>Baseado na Regra de Lipinski para predizer drug-likeness</em>
            </p>
        </div>"""
        
        return tabela, analise_html
    except Exception as e:
        return "", f"<p style='color: #e74c3c;'>Erro ao processar propriedades: {str(e)[:100]}</p>"


def discover_assets(pasta: Path) -> list:
    """Descobre arquivos gerados"""
    files = []
    
    if not pasta.exists():
        return files
    
    for file in sorted(pasta.glob('*')):
        if file.is_file() and file.name not in ['relatorio_final.html', 'Relatorio_Final_Dashboard.md', 'manifest.json']:
            files.append(file.name)
    
    return files


def gerar_html_simples(pasta: Path, drug_name: str) -> str:
    """Gera HTML simples e direto"""
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    projeto = pasta.name
    energia = ler_energia_vina(pasta)
    interacoes = ler_interacoes_plip(pasta)
    props_tabela, props_analise = ler_propriedades_quimicas(pasta)
    arquivos = discover_assets(pasta)
    
    # Lista de arquivos
    arquivos_html = "".join([
        f'<li><a href="./{arq}" target="_blank">{arq}</a></li>'
        for arq in arquivos
    ])
    
    # Imagens
    imagens = [f for f in arquivos if f.endswith(('.png', '.jpg', '.jpeg'))]
    imagens_html = "".join([
        f'<figure style="text-align: center; margin: 20px 0;">'
        f'<img src="./{img}" style="max-width: 600px; border: 1px solid #ccc; border-radius: 5px;">'
        f'<figcaption style="font-size: 0.9em; color: #666; margin-top: 5px;">{img}</figcaption>'
        f'</figure>'
        for img in imagens
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Docking - {projeto}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-top: 0;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #ecf0f1;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
            color: #2980b9;
        }}
        .info-box {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 12px;
            margin: 15px 0;
            border-radius: 3px;
        }}
        .energy {{
            color: #27ae60;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Docking Molecular</h1>
        
        <div class="info-box">
            <strong>Projeto:</strong> {projeto}<br>
            <strong>Fármaco:</strong> {drug_name}<br>
            <strong>Gerado em:</strong> {timestamp}
        </div>
        
        <h2>1. Afinidade de Ligação</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Energia de Ligação (AutoDock Vina)</td>
                <td class="energy">{energia}</td>
            </tr>
        </table>
        
        <h2>2. Propriedades Químicas</h2>
        <table>
            <tr>
                <th>Propriedade</th>
                <th>Valor</th>
            </tr>
            {props_tabela if props_tabela else '<tr><td colspan="2">RDKit não disponível</td></tr>'}
        </table>
        
        <h2>3. Avaliação de Drug-Likeness (Regra de Lipinski)</h2>
        {props_analise if props_analise else '<p>Análise não disponível</p>'}
        
        <h2>4. Interações Proteína-Ligante (PLIP)</h2>
        {interacoes}
        
        {"<h2>5. Estrutura 2D do Fármaco</h2>" + imagens_html if imagens_html else ""}
        
        <h2>{'6. ' if imagens_html else '5. '}Arquivos Gerados</h2>
        <ul>
            {arquivos_html if arquivos_html else '<li>Nenhum arquivo adicional encontrado</li>'}
        </ul>
        
        <div class="footer">
            <p>Relatório gerado automaticamente pelo sistema de bioinformática</p>
            <p>{timestamp}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 gerar_relatorio_final.py <pasta_trabalho> [nome_droga]")
        sys.exit(1)
    
    pasta = Path(sys.argv[1])
    drug_name = sys.argv[2] if len(sys.argv) > 2 else pasta.name.split('_')[-1]
    
    if not pasta.exists():
        print(f"❌ Pasta não encontrada: {pasta}")
        sys.exit(1)
    
    print(f"[Relatório] Processando: {pasta}")
    
    # Gerar HTML
    html_content = gerar_html_simples(pasta, drug_name)
    
    # Salvar HTML
    html_path = pasta / "relatorio_final.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Relatório salvo: {html_path}")
