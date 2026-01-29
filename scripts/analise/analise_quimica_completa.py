import sys
import os
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, QED, Lipinski

def analisar_molecula(pasta_trabalho, droga):
    """✅ CORRIGIDO: Busca arquivo SDF na pasta de trabalho"""
    # Construir caminho do arquivo SDF na pasta de trabalho
    sdf_path = os.path.join(pasta_trabalho, f"{droga}.sdf")
    
    print(f"--- Lendo molécula: {sdf_path} ---")
    
    if not os.path.exists(sdf_path):
        print(f"❌ Erro: Arquivo SDF não encontrado em {sdf_path}")
        return
    
    # O RDKit às vezes reclama de SDFs "sujos", o sanitize=False ajuda a ler mesmo assim
    suppl = Chem.SDMolSupplier(sdf_path, sanitize=False)
    mol = next(suppl)
    
    if mol is None:
        print("Erro: RDKit não conseguiu ler a estrutura no SDF.")
        return

    # Tenta consertar a molécula (cargas, valência) para calcular certo
    try:
        Chem.SanitizeMol(mol)
    except:
        print("Aviso: Falha ao sanitizar molécula. Resultados podem ser imprecisos.")

    print(f"Molécula processada com sucesso. Calculando propriedades...\n")

    # --- 1. Propriedades Físico-Químicas ---
    mw = Descriptors.MolWt(mol)           # Peso Molecular
    logp = Descriptors.MolLogP(mol)       # Lipofilicidade
    hbd = Lipinski.NumHDonors(mol)        # Doadores de H
    hba = Lipinski.NumHAcceptors(mol)     # Aceitadores de H
    tpsa = Descriptors.TPSA(mol)          # Área Polar (Habilidade de cruzar membranas)
    rotatable = Lipinski.NumRotatableBonds(mol) # Flexibilidade
    qed_score = QED.qed(mol)              # Drug-likeness (0 a 1)

    # --- 2. O Veredito (Relatório) ---
    print("="*40)
    print(f" RELATÓRIO DE QUÍMICA MEDICINAL")
    print("="*40)
    print(f"Nome do Arquivo: {os.path.basename(sdf_path)}")
    print("-" * 40)
    
    # Regra de Lipinski (Regra dos 5)
    print(f"[Regra de Lipinski] (Biodisponibilidade Oral)")
    print(f"  - Peso Molecular : {mw:.2f} \t(Ideal < 500)")
    print(f"  - LogP (Gordura) : {logp:.2f} \t(Ideal < 5)")
    print(f"  - H-Bond Donors  : {hbd}    \t(Ideal < 5)")
    print(f"  - H-Bond Acceptors: {hba}   \t(Ideal < 10)")
    
    violacoes = 0
    if mw > 500: violacoes += 1
    if logp > 5: violacoes += 1
    if hbd > 5: violacoes += 1
    if hba > 10: violacoes += 1
    
    print(f"  >> Violações: {violacoes}/4")
    if violacoes <= 1: print("     STATUS: APROVADO (Boa chance oral)")
    else: print("     STATUS: ALERTA (Molécula difícil absorção)")

    print("-" * 40)
    
    # Regra de Veber (Absorção Intestinal)
    print(f"[Regra de Veber] (Permeabilidade)")
    print(f"  - TPSA           : {tpsa:.2f} Å²\t(Ideal < 140)")
    print(f"  - Rotatable Bonds: {rotatable}  \t(Ideal < 10)")
    
    passou_veber = (tpsa <= 140) and (rotatable <= 10)
    if passou_veber: print("     STATUS: APROVADO (Boa permeabilidade)")
    else: print("     STATUS: ALERTA (Muito flexível ou polar demais)")

    print("-" * 40)
    
    # Score Geral (QED)
    print(f"[Índice QED] (Drug-likeness)")
    print(f"  - Score: {qed_score:.3f} (0=Ruim, 1=Perfeito)")
    if qed_score > 0.6: print("     STATUS: Excelente candidato a fármaco.")
    elif qed_score > 0.4: print("     STATUS: Razoável.")
    else: print("     STATUS: Baixa similaridade com fármacos conhecidos.")
    print("="*40)

    # --- 3. Gerar Imagem ---
    nome_imagem = sdf_path.replace(".sdf", "_2D_structure.png")
    print(f"\nGerando imagem estrutural: {nome_imagem}...")
    Draw.MolToFile(mol, nome_imagem, size=(600, 600))
    print("Sucesso! Imagem salva.")

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 analise_quimica_completa.py <pasta_trabalho> <nome_droga>")
        sys.exit(1)
    
    pasta_trabalho = sys.argv[1]
    droga = sys.argv[2]
    
    if os.path.exists(pasta_trabalho):
        analisar_molecula(pasta_trabalho, droga)
    else:
        print(f"Erro: Pasta não encontrada: {pasta_trabalho}")
        sys.exit(1)
