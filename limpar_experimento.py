import os
import sys

def limpar_pasta(pasta):
    # Lista de extensões que podem ser apagadas sem medo
    extensoes_limpar = ['.pdbqt', '.txt', '.log', '.html', '.md', '.png']
    
    if not os.path.exists(pasta):
        print(f"❌ Pasta {pasta} não encontrada.")
        return

    print(f"🧹 Limpando arquivos temporários em: {pasta}")
    for f in os.listdir(pasta):
        if any(f.endswith(ext) for ext in extensoes_limpar):
            # NÃO apaga o arquivo original da proteína ou ligante (PDB/SDF)
            if not (f.endswith('.pdb') or f.endswith('.sdf')):
                os.remove(os.path.join(pasta, f))
    print("✅ Pasta limpa! Pronta para novo teste de precisão.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 limpar_experimento.py <PASTA>")
    else:
        limpar_pasta(sys.argv[1])