import sys
import os
import subprocess

def log(mensagem):
    print(f"[QUÍMICA-3D] {mensagem}")

def converter_para_3d(arquivo_entrada):
    nome_base = os.path.splitext(arquivo_entrada)[0]
    arquivo_saida = f"{nome_base}_3D_minimizado.sdf"

    # Remove arquivos residuais de tentativas falhas
    if os.path.exists(arquivo_saida): os.remove(arquivo_saida)

    log(f"Iniciando conversão de {arquivo_entrada} para 3D...")

    try:
        # PASSO 1: Gera coordenadas 3D com algoritmo mais robusto
        # Adicionei --errorlevel 1 para debug e removi o temp para ser mais direto
        subprocess.run([
            "obabel", arquivo_entrada, 
            "-osdf", "-O", arquivo_saida, 
            "--gen3d", "best", # Tenta a melhor conformação possível
            "--errorlevel", "1"
        ], check=True)

        # Validação de Segurança: O arquivo tem conteúdo?
        if not os.path.exists(arquivo_saida) or os.path.getsize(arquivo_saida) == 0:
            log("❌ Erro: OpenBabel gerou um arquivo vazio. Verifique o arquivo 2D.")
            return None

        # PASSO 2: Minimização de Energia
        log("Refinando estrutura (Minimização MMFF94 - 500 passos)...")
        subprocess.run([
            "obabel", arquivo_saida, 
            "-osdf", "-O", arquivo_saida, 
            "--minimize", "--steps", "500", "--ff", "MMFF94"
        ], check=True)

        log(f"✅ SUCESSO! Ligante 3D pronto: {arquivo_saida}")
        return arquivo_saida

    except Exception as e:
        log(f"❌ Erro Crítico: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 preparar_ligante_3d.py <arquivo_2d.sdf_ou_pdb>")
    else:
        converter_para_3d(sys.argv[1])