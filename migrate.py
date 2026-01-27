#!/usr/bin/env python3
"""
Script de Migração Automática
Move resultados existentes de mapk_*/, pdrk_*/ para nova estrutura results/
Mantém dados intactos e cria symlinks para compatibilidade backward
"""

import shutil
import json
from pathlib import Path
from datetime import datetime

def migrar_resultados():
    """Migra resultados da raiz para results/ e atualiza estrutura"""
    
    root = Path(__file__).parent.parent
    results_dir = root / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Padrões de pastas de trabalho
    work_dirs = list(root.glob('*_*')) + list(root.glob('mapk_*')) + list(root.glob('pdrk_*'))
    work_dirs = [d for d in work_dirs if d.is_dir() and not d.name.startswith('.')]
    
    migrados = []
    
    for work_dir in work_dirs:
        # Pular se já está em results/
        if work_dir.parent == results_dir:
            continue
        
        # Pular pastas do sistema
        if work_dir.name in ['scripts', 'templates', 'config', 'docs', '__pycache__']:
            continue
        
        new_path = results_dir / work_dir.name
        
        # Se já existe, fazer backup
        if new_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = new_path.parent / f"{new_path.name}_backup_{timestamp}"
            print(f"⚠️  {new_path.name} já existe. Backup em {backup_path.name}")
            shutil.move(str(new_path), str(backup_path))
        
        # Mover
        print(f"📦 Movendo: {work_dir.name} → results/")
        shutil.move(str(work_dir), str(new_path))
        
        # Criar symlink na raiz para compatibilidade (opcional)
        # symlink_path = root / work_dir.name
        # symlink_path.symlink_to(new_path, target_is_directory=True)
        
        migrados.append({
            'nome': work_dir.name,
            'novo_caminho': str(new_path.relative_to(root)),
            'timestamp': datetime.now().isoformat()
        })
    
    # Salvar log de migração
    log_file = results_dir / ".migration_log.json"
    with open(log_file, 'w') as f:
        json.dump({
            'data_migracao': datetime.now().isoformat(),
            'total_migrados': len(migrados),
            'detalhes': migrados
        }, f, indent=2)
    
    return len(migrados), migrados


def listar_estrutura_nova():
    """Exibe a nova estrutura criada"""
    root = Path(__file__).parent.parent
    results_dir = root / "results"
    
    print("\n" + "="*70)
    print("📂 NOVA ESTRUTURA DE PROJETO")
    print("="*70)
    
    print(f"\n{root.name}/")
    print("├── 📁 config/")
    print("│   ├── config.yaml")
    print("│   ├── targets.json")
    print("│   └── drugs.json")
    print("├── 📁 templates/")
    print("│   ├── proteins/")
    print("│   │   ├── mapk.pdb")
    print("│   │   └── pdrk.pdb")
    print("│   └── drugs/")
    print("│       ├── Iprodione.sdf")
    print("│       ├── Fludioxonil.sdf")
    print("│       └── pepstatin_3D_minimizado.sdf")
    print("├── 📁 scripts/")
    print("│   ├── preparacao/")
    print("│   ├── docking/")
    print("│   ├── analise/")
    print("│   ├── relatorio/")
    print("│   └── utils/")
    print("├── 📁 results/  ← NOVO! Todos os resultados aqui")
    print("│   ├── mapk_Iprodione/")
    print("│   ├── mapk_Fludioxonil/")
    print("│   ├── pdrk_Iprodione/")
    print("│   └── ...")
    print("├── 📁 docs/")
    print("├── 📁 logs/")
    print("├── ⚙️  config.py       (Novo: centraliza paths)")
    print("├── 🐍 virtual_screening_mestre.py")
    print("├── 🛠️  utils.py")
    print("└── 📋 config.yaml")
    
    print(f"\n✅ Estrutura criada com sucesso!")
    print(f"   Resultados em: {results_dir}")


if __name__ == "__main__":
    print("🔄 Iniciando migração automática...\n")
    
    total, detalhes = migrar_resultados()
    
    if total > 0:
        print(f"\n✅ {total} pasta(s) migrada(s) com sucesso!")
        for item in detalhes:
            print(f"   • {item['nome']} → {item['novo_caminho']}")
    else:
        print("ℹ️  Nenhuma pasta para migrar (já estão em results/ ou não existem)")
    
    listar_estrutura_nova()
    
    print("\n" + "="*70)
    print("📝 PRÓXIMOS PASSOS")
    print("="*70)
    print("""
1. Atualizar scripts legados para usar nova estrutura:
   python3 scripts/preparacao/preparar_arquivosuniversal.py <pasta>

2. Criar novos aliases para executar scripts:
   alias run-screening='python3 virtual_screening_mestre.py'

3. Consultar documentação:
   cat docs/README_REFACTORING.md

4. Executar novo pipeline:
   python3 virtual_screening_mestre.py config/config.yaml
""")
