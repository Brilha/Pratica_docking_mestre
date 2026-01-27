import sys
from Bio.PDB import PDBParser, PPBuilder

def buscar_sequencia_no_pdb(arquivo_pdb, sequencia_alvo):
    parser = PDBParser(QUIET=True)
    estrutura = parser.get_structure('alvo', arquivo_pdb)
    ppb = PPBuilder()
    
    print(f"--- Buscando motivo: {sequencia_alvo} ---")
    
    encontrado = False
    for pp in ppb.build_peptides(estrutura):
        seq_completa = pp.get_sequence()
        posicao = seq_completa.find(sequencia_alvo)
        
        if posicao != -1:
            # O BioPython numera começando do 0, ajustamos para o número do PDB
            inicio_res = pp[posicao].get_id()[1]
            fim_res = pp[posicao + len(sequencia_alvo) - 1].get_id()[1]
            print(f"✅ MOTIVO ENCONTRADO!")
            print(f"   -> Resíduos: {inicio_res} até {fim_res}")
            print(f"   -> Cadeia: {pp[0].get_full_id()[2]}")
            encontrado = True
            
    if not encontrado:
        print("❌ Sequência não encontrada nesta proteína.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 buscar_motivo.py <arquivo.pdb> <SEQUENCIA>")
    else:
        buscar_sequencia_no_pdb(sys.argv[1], sys.argv[2].upper())