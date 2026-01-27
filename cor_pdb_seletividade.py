import sys
import os
from Bio import SeqIO
from Bio.PDB import PDBParser, PDBIO, Select
from Bio.Blast import NCBIWWW, NCBIXML

# --- 0. Dicionário Manual (À prova de falhas) ---
# Traduz aminoácidos de 3 letras (PDB) para 1 letra (Sequência)
aa_3to1 = {
    'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F', 
    'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L', 
    'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R', 
    'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'
}

# --- 1. Classes e Funções Auxiliares ---

class SomenteProteina(Select):
    """Filtra para salvar apenas aminoácidos padrão no PDB final."""
    def accept_residue(self, residue):
        # Aceita apenas resíduos que não são HETATM e estão no nosso dicionário
        return residue.id[0] == " " and residue.get_resname() in aa_3to1

def extrair_sequencia_e_numeracao(structure):
    """Extrai a sequência e mapeia o índice da sequência para o número do resíduo no PDB."""
    seq = ""
    pdb_res_nums = []
    
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0] == " ": # Apenas aminoácidos padrão
                    res_nome = residue.get_resname() # Ex: 'ALA'
                    
                    # Usa nosso dicionário manual
                    if res_nome in aa_3to1:
                        seq += aa_3to1[res_nome]
                        pdb_res_nums.append(residue.id[1]) # Guarda o número original
                    else:
                        print(f"   [Aviso] Resíduo ignorado (não padrão): {res_nome}")
                        
            break # Pega apenas a primeira cadeia
        break # Pega apenas o primeiro modelo
        
    return str(seq), pdb_res_nums

# --- 2. O Coração do Processo (BLAST e Mapeamento) ---

def mapear_identidade_humana(sequencia):
    print("\n--- Iniciando BLASTp contra Homo sapiens (Aguarde...) ---")
    try:
        # Roda BLAST contra SwissProt humano
        result_handle = NCBIWWW.qblast(
            "blastp", 
            "swissprot", 
            sequencia, 
            entrez_query="Homo sapiens[Organism]", 
            hitlist_size=1, 
            expect=10.0
        )
    except Exception as e:
        print(f"Erro de conexão com o NCBI: {e}")
        sys.exit()
        
    print("BLAST concluído! Processando alinhamento...")
    blast_record = NCBIXML.read(result_handle)
    
    if not blast_record.alignments:
        print(">>> Nenhum hit humano significativo encontrado. Proteína altamente seletiva!")
        return [0.0] * len(sequencia)

    hsp = blast_record.alignments[0].hsps[0]
    print(f"Melhor hit humano: {blast_record.alignments[0].title[:40]}...")
    print(f"Identidade global: {(hsp.identities/hsp.align_length)*100:.1f}%")

    # Cria o mapa de identidade (0.0 = Seguro, 100.0 = Perigo)
    mapa_scores = [0.0] * len(sequencia)
    
    start_index = hsp.query_start - 1 
    
    for i, char_match in enumerate(hsp.match):
        seq_index = start_index + i
        if seq_index < len(mapa_scores):
            if char_match == '|':
                mapa_scores[seq_index] = 100.0 # Idêntico -> Vermelho
            elif char_match == '+':
                 mapa_scores[seq_index] = 50.0 # Similar -> Amarelo
            
    return mapa_scores

# --- 3. Modificação do PDB ---

def criar_pdb_colorido(pdb_input, pdb_output, scores, pdb_res_nums):
    print(f"\n--- Injetando scores de seletividade no B-factor ---")
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("alvo_colorido", pdb_input)
    
    residue_count = 0
    total_modificados = 0
    
    for model in structure:
        for chain in model:
            for residue in chain:
                # Checa se é aminoácido padrão usando nosso dicionário
                if residue.id[0] == " " and residue.get_resname() in aa_3to1:
                    if residue_count < len(scores):
                        score_atual = scores[residue_count]
                        
                        # Injeta o score no B-factor de cada átomo
                        for atom in residue:
                            atom.set_bfactor(score_atual)
                        
                        total_modificados += 1
                    residue_count += 1
            break 
        break 
        
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdb_output, select=SomenteProteina())
    print(f">>> SUCESSO: Arquivo gerado: {pdb_output}")
    print(f"Total de resíduos mapeados: {total_modificados}")
    print("Abra no Chimera e use: Tools -> Depiction -> Render by Attribute (residues -> average bfactor)")

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 cor_pdb_seletividade.py <arquivo_pdb_limpo>")
        sys.exit()
        
    pdb_input = sys.argv[1]
    if not os.path.exists(pdb_input):
        print(f"Erro: Arquivo {pdb_input} não encontrado.")
        sys.exit()
        
    path, ext = os.path.splitext(pdb_input)
    pdb_output = f"{path}_seletividade.pdb"
    
    # 1. Lê estrutura
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("temp", pdb_input)
    
    # 2. Extrai sequência
    sequencia_str, pdb_numeros = extrair_sequencia_e_numeracao(structure)
    print(f"Sequência extraída ({len(sequencia_str)} resíduos): {sequencia_str[:10]}...")
    
    # 3. Roda BLAST
    scores_seletividade = mapear_identidade_humana(sequencia_str)
    
    # 4. Gera PDB final
    criar_pdb_colorido(pdb_input, pdb_output, scores_seletividade, pdb_numeros)