import os
import pandas as pd

def gerar_ranking():
    dados = []
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and "_" in d]
    
    for pasta in pastas:
        log_vina = os.path.join(pasta, "log_docking.txt")
        if os.path.exists(log_vina):
            with open(log_vina, 'r') as f:
                for line in f:
                    if line.strip().startswith("1"):
                        energia = float(line.split()[1])
                        alvo, droga = pasta.split('_', 1)
                        dados.append({"Alvo": alvo, "Droga": droga, "Energia (kcal/mol)": energia})
                        break
    
    if dados:
        df = pd.DataFrame(dados).sort_values(by="Energia (kcal/mol)")
        df.to_csv("ranking_final.csv", index=False)
        print("🏆 Ranking gerado em 'ranking_final.csv'!")
        print(df.to_string(index=False))
    else:
        print("Nenhum resultado encontrado para o ranking.")

if __name__ == "__main__":
    gerar_ranking()