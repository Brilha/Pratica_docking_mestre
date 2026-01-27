import os
import shutil

def faxina_geral():
    caminho = os.getcwd()
    pastas = [d for d in os.listdir(caminho) if os.path.isdir(d) and ("_" in d)]
    
    print(f"--- Iniciando limpeza em {len(pastas)} pastas ---")
    
    removidas = 0
    for pasta in pastas:
        # Critério de sucesso: tem que ter o relatório final
        relatorio = os.path.join(pasta, "Relatorio_Final_Dashboard.md")
        if not os.path.exists(relatorio):
            print(f"🗑️ Removendo pasta incompleta: {pasta}")
            shutil.rmtree(pasta)
            removidas += 1
            
    print(f"\n✨ Faxina concluída! {removidas} pastas inúteis foram removidas.")

if __name__ == "__main__":
    faxina_geral()