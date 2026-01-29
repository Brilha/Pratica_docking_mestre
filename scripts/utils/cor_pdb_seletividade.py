import sys
import os
import subprocess
import tempfile
from pathlib import Path
from Bio import SeqIO
from Bio.PDB import PDBParser, PDBIO, Select

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

# --- 2. O Coração do Processo (BLAST LOCAL e Mapeamento) ---

def extrair_sequencia_fasta(pdb_file):
    """Extrai sequência do PDB e salva em arquivo FASTA temporário"""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("temp", pdb_file)
    
    seq = ""
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0] == " " and residue.get_resname() in aa_3to1:
                    seq += aa_3to1[residue.get_resname()]
            break
        break
    
    return seq

def mapear_identidade_humana(sequencia):
    """
    ✅ NOVO: Usa BLAST LOCAL com proteína humana em templates/proteinas_humanas/
    Em vez de NCBIWWW.qblast() remoto (que leva 10-20 min)
    Agora usa blastp local (1-2 segundos)
    """
    
    # ✅ NOVO: Caminho da proteína humana local
    PROTEINA_HUMANA = Path(__file__).parent.parent.parent / "templates" / "proteinas_humanas" / "hctr1.pdb"
    
    print(f"\n--- Iniciando BLASTp LOCAL contra proteína humana ---")
    print(f"Proteína humana: {PROTEINA_HUMANA}")
    
    if not PROTEINA_HUMANA.exists():
        print(f"⚠️  Arquivo não encontrado: {PROTEINA_HUMANA}")
        print(f"   Usando sequência sem comparação (scores zerados)")
        return [0.0] * len(sequencia)
    
    # Extrai sequência da proteína humana
    try:
        seq_humana = extrair_sequencia_fasta(str(PROTEINA_HUMANA))
    except Exception as e:
        print(f"⚠️  Erro ao extrair sequência humana: {e}")
        return [0.0] * len(sequencia)
    
    print(f"Sequência humana extraída: {len(seq_humana)} resíduos")
    
    # ✅ NOVO: Salva sequências em arquivos FASTA temporários
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f_query:
        f_query.write(f">target\n{sequencia}\n")
        fasta_query = f_query.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f_subject:
        f_subject.write(f">human\n{seq_humana}\n")
        fasta_subject = f_subject.name
    
    try:
        # ✅ NOVO: Cria banco de dados FASTA local (rápido)
        print("Criando banco de dados BLAST local...")
        subprocess.run(
            ["makeblastdb", "-in", fasta_subject, "-dbtype", "prot", "-out", "/tmp/human_db"],
            capture_output=True,
            timeout=10
        )
        
        # ✅ NOVO: Executa BLAST contra banco local
        print("Executando BLASTp local...")
        result = subprocess.run(
            ["blastp", "-query", fasta_query, "-db", "/tmp/human_db", 
             "-outfmt", "6 qseq sseq", "-max_target_seqs", "1"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            print(">>> Nenhum hit humano significativo encontrado. Proteína altamente seletiva!")
            return [0.0] * len(sequencia)
        
        # ✅ NOVO: Processa resultado do BLAST
        lines = result.stdout.strip().split('\n')
        if lines:
            parts = lines[0].split('\t')
            if len(parts) >= 2:
                qseq = parts[0]  # Sequência query
                sseq = parts[1]  # Sequência subject
                
                # Cria mapa de identidade
                mapa_scores = [0.0] * len(sequencia)
                
                # Alinha caractere por caractere
                for i, (q, s) in enumerate(zip(qseq, sseq)):
                    if i < len(mapa_scores):
                        if q == s:
                            mapa_scores[i] = 100.0  # Idêntico -> Vermelho
                        elif q.upper() == s.upper():
                            mapa_scores[i] = 50.0   # Similar -> Amarelo
                        else:
                            mapa_scores[i] = 0.0    # Diferente -> Azul
                
                # Calcula % identidade
                identicos = sum(1 for q, s in zip(qseq, sseq) if q == s)
                pct_ident = (identicos / len(qseq) * 100) if qseq else 0
                
                print(f"✅ Alinhamento encontrado!")
                print(f"   Comprimento: {len(qseq)} resíduos")
                print(f"   Identidade: {pct_ident:.1f}%")
                
                return mapa_scores
        
        return [0.0] * len(sequencia)
    
    except subprocess.TimeoutExpired:
        print("⚠️  BLAST timeout. Usando scores padrão (zerados).")
        return [0.0] * len(sequencia)
    except Exception as e:
        print(f"⚠️  Erro na execução do BLAST: {e}")
        return [0.0] * len(sequencia)
    finally:
        # Limpa arquivos temporários
        try:
            os.remove(fasta_query)
            os.remove(fasta_subject)
        except:
            pass

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
        print("Uso: python3 cor_pdb_seletividade.py <pasta_trabalho>")
        sys.exit()
        
    pasta_trabalho = sys.argv[1]
    
    # ✅ MODULÁVEL: Procura automaticamente por arquivo *_clean.pdb
    arquivos = os.listdir(pasta_trabalho)
    pdb_input_name = next((f for f in arquivos if f.endswith("_clean.pdb")), None)
    
    if pdb_input_name is None:
        print(f"Erro: Nenhum arquivo *_clean.pdb encontrado em {pasta_trabalho}")
        sys.exit()
    
    pdb_input = os.path.join(pasta_trabalho, pdb_input_name)
    
    # ✅ FIX (28/Jan): Previne reprocessamento de arquivos já coloridos
    # Evita criar ctr3_seletividade_seletividade.pdb quando arquivo já tem _seletividade
    if "_seletividade" in pdb_input_name and "_clean.pdb" in pdb_input_name:
        print(f"\n⚠️  Arquivo já foi processado: {pdb_input_name}")
        print(f"Pulando para evitar recursão (ex: *_seletividade_seletividade.pdb)")
        sys.exit()
    
    # ✅ MODULÁVEL: Nome da saída derivado do arquivo limpo
    base_name = pdb_input_name.replace("_clean.pdb", "")  # Remove _clean.pdb
    pdb_output = os.path.join(pasta_trabalho, f"{base_name}_seletividade.pdb")
    
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