#!/usr/bin/env python3
"""
Gerar Relatório Final Integrado com Dashboard
VERSÃO REFATORADA: Descobre automaticamente imagens, HTML e arquivos interativos
Gera markdown com links e embeddings corretos de assets
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, QED
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False


def discover_assets(pasta: Path) -> dict:
    """
    Descobre automaticamente todos os assets gerados (imagens, HTML, PSE, etc)
    
    Returns:
        Dict com caminhos para cada tipo de asset encontrado
    """
    assets = {
        'images': [],
        'html_interactive': [],
        'pse_files': [],
        'report_files': [],
        'config_files': [],
        'docking_log': None,
    }
    
    if not pasta.exists():
        return assets
    
    for file in pasta.glob('*'):
        if file.suffix == '.png':
            assets['images'].append(file.name)
        elif file.suffix == '.html':
            assets['html_interactive'].append(file.name)
        elif file.suffix == '.pse':
            assets['pse_files'].append(file.name)
        elif 'report' in file.name and file.suffix == '.txt':
            assets['report_files'].append(file.name)
        elif file.name == 'config.txt':
            assets['config_files'].append(file.name)
        elif 'log' in file.name.lower() and file.suffix == '.txt':
            assets['docking_log'] = file.name
    
    return assets


def ler_energia_vina(pasta: Path) -> str:
    """Lê energia de ligação do log de docking do Vina"""
    # Procurar por arquivos de log
    log_files = list(pasta.glob('log*.txt'))
    
    if not log_files:
        return "N/A (Log não encontrado)"
    
    caminho_log = log_files[0]
    
    try:
        with open(caminho_log, 'r') as f:
            for line in f:
                # Procura a linha da primeira pose (mode 1)
                if line.strip().startswith("1 "):
                    partes = line.split()
                    if len(partes) >= 2:
                        return f"{partes[1]} kcal/mol"
    except Exception as e:
        return f"Erro ao ler log: {e}"
    
    return "N/A"


def ler_interacoes_plip(pasta: Path) -> str:
    """Lê resumo de interações do relatório PLIP"""
    # Procurar por arquivos de report
    report_files = list(pasta.glob('*report*.txt'))
    
    if not report_files:
        return "Relatório PLIP não encontrado."
    
    caminho = report_files[0]
    resumo = {}
    
    try:
        with open(caminho, 'r') as f:
            texto = f.read()
            # Conta ocorrências das palavras chave do PLIP
            resumo['Hydrophobic Interactions'] = texto.count('Hydrophobic Interaction')
            resumo['Hydrogen Bonds'] = texto.count('Hydrogen Bond')
            resumo['Pi-Stacking'] = texto.count('pi-Stacking')
            resumo['Salt Bridges'] = texto.count('Salt Bridge')
    except Exception as e:
        return f"Erro ao ler relatório: {e}"
    
    txt_saida = ""
    for tipo, qtd in resumo.items():
        if qtd > 0:
            txt_saida += f"- {tipo}: {qtd}\n"
    
    if not txt_saida:
        return "Nenhuma interação detectada."
    return txt_saida


def ler_propriedades_quimicas(pasta: Path, drug_name: str) -> str:
    """Lê propriedades químicas da droga"""
    sdf_files = list(pasta.glob('*.sdf'))
    
    if not sdf_files:
        return "Arquivo SDF não encontrado."
    
    if not HAS_RDKIT:
        return "RDKit não disponível para análise de propriedades."
    
    sdf_path = sdf_files[0]
    
    try:
        mol = Chem.SDMolBlockToMol(open(sdf_path).read())
        if mol is None:
            return "Erro ao parsear molécula."
        
        props = f"""
- **Peso Molecular:** {Descriptors.MolWt(mol):.2f} g/mol
- **LogP:** {Descriptors.MolLogP(mol):.2f}
- **Doadores H:** {Descriptors.NumHDonors(mol)}
- **Aceitadores H:** {Descriptors.NumHAcceptors(mol)}
- **Rotáveis:** {Descriptors.NumRotatableBonds(mol)}
- **QED Score:** {QED.qed(mol):.3f}
- **Lipinski OK:** {'✅ Sim' if Lipinski.NumHDonors(mol) <= 5 else '❌ Não'}
"""
        return props.strip()
    except Exception as e:
        return f"Erro ao processar SDF: {e}"


def gerar_markdown_com_assets(pasta: Path, assets: dict, drug_name: str) -> str:
    """
    Gera markdown markdown integrado com imagens e links corretos
    
    NOVO: Incorpora automaticamente:
    - Imagens PNG com ![](./file.png) syntax
    - Links para HTML interativo
    - Links para sessões PyMOL (.pse)
    - Links para relatórios textuais
    """
    trabalho_dir = pasta.name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    energia = ler_energia_vina(pasta)
    interacoes = ler_interacoes_plip(pasta)
    propriedades = ler_propriedades_quimicas(pasta, drug_name)
    
    # Iniciar markdown
    markdown = f"""# 📄 Relatório Integrado de Bioinformática

**Projeto:** {trabalho_dir}  
**Data:** {timestamp}  
**Fármaco:** {drug_name}

---

## 1. 🎯 Resumo de Docking

### Afinidade de Ligação
**Energia Vina:** {energia}

### Interações Detectadas (PLIP)
{interacoes}

---

## 2. 🧪 Propriedades Químicas do Fármaco

{propriedades}

---

## 3. 📊 Visualizações Geradas

"""
    
    # Seção: Estrutura 3D (PyMOL)
    if assets['pse_files']:
        markdown += "### 3️⃣ Complexo 3D (PyMOL)\n\n"
        for pse_file in assets['pse_files']:
            markdown += f"[📥 Abrir em PyMOL: {pse_file}](./{pse_file})\n\n"
    else:
        markdown += "### 3️⃣ Complexo 3D (PyMOL)\n\n"
        markdown += "Nenhum arquivo .pse encontrado.\n\n"
    
    # Seção: Estrutura 2D (Imagem química)
    if assets['images']:
        markdown += "### 2️⃣ Estrutura Química (2D)\n\n"
        for img_file in assets['images']:
            markdown += f"![Estrutura 2D](./{img_file})\n\n"
    
    # Seção: Interações Interativas (ProLIF HTML)
    if assets['html_interactive']:
        markdown += "### 🔗 Mapa de Interações (ProLIF Interativo)\n\n"
        for html_file in assets['html_interactive']:
            markdown += f"[🔍 Abrir diagrama interativo](./{html_file})\n\n"
    
    # Seção: Arquivos de Relatório
    if assets['report_files']:
        markdown += "### 📝 Relatórios Detalhados\n\n"
        for report_file in assets['report_files']:
            markdown += f"[📄 {report_file}](./{report_file})\n\n"
    
    # Seção: Configuração de Docking
    if assets['config_files']:
        markdown += "### ⚙️ Configuração de Docking\n\n"
        for config_file in assets['config_files']:
            markdown += f"[🔧 {config_file}](./{config_file})\n\n"
    
    # Rodapé com metadados
    markdown += f"""
---

## 📂 Metadados

- **Diretório de saída:** {pasta.absolute()}
- **Total de arquivos:** {len(list(pasta.glob('*')))}
- **Arquivos descobertos:**
  - Imagens: {len(assets['images'])}
  - HTML interativo: {len(assets['html_interactive'])}
  - Sessões PyMOL: {len(assets['pse_files'])}
  - Relatórios: {len(assets['report_files'])}

---

**Gerado automaticamente em {timestamp}**
"""
    
    return markdown


def salvar_manifest(pasta: Path, assets: dict):
    """
    Salva manifest.json com lista de arquivos descobertos
    Útil para scripts posteriores localizarem assets
    """
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'work_dir': str(pasta.absolute()),
        'assets': assets,
    }
    
    manifest_path = pasta / 'manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    return manifest_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 gerar_relatorio_final.py <pasta_trabalho> [nome_droga]")
        sys.exit(1)
    
    pasta = Path(sys.argv[1])
    drug_name = sys.argv[2] if len(sys.argv) > 2 else pasta.name.split('_')[-1]
    
    if not pasta.exists():
        print(f"❌ Pasta não encontrada: {pasta}")
        sys.exit(1)
    
    print(f"[Dashboard] Processando: {pasta}")
    
    # Descobrir assets
    assets = discover_assets(pasta)
    print(f"[Dashboard] Descobertos {len(assets['images'])} imagens, "
          f"{len(assets['html_interactive'])} HTML, "
          f"{len(assets['pse_files'])} .pse")
    
    # Gerar markdown
    markdown_content = gerar_markdown_com_assets(pasta, assets, drug_name)
    
    # Salvar markdown
    markdown_path = pasta / "Relatorio_Final_Dashboard.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Markdown salvo: {markdown_path}")
    
    # Salvar manifest
    manifest_path = salvar_manifest(pasta, assets)
    print(f"✅ Manifest salvo: {manifest_path}")
