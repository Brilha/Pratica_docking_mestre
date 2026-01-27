import MDAnalysis as mda
import prolif as plf
import os
import sys

def gerar_mapa_2d(pasta):
    # Localiza arquivos
    receptor = os.path.join(pasta, "receptor.pdbqt") # Precisa ser PDB para o MDAnalysis
    ligante = os.path.join(pasta, "resultado_docking.pdbqt")
    
    # Carrega no motor ProLIF
    u = mda.Universe(receptor, ligante)
    prot = u.select_atoms("protein")
    lig = u.atoms.select_atoms("resname UNL or resname LIG") # O Vina geralmente chama de UNL
    
    fp = plf.Fingerprint()
    fp.run(u.trajectory[0:1], lig, prot)
    
    # Gera o HTML interativo
    df = fp.to_dataframe()
    net = fp.plot_lignetwork(u.trajectory[0], lig)
    net.save(os.path.join(pasta, "interacao_2d_interativa.html"))
    print(f"✅ Mapa 2D interativo salvo em {pasta}")

# Nota: Este script exige que os arquivos estejam em formato PDB/SDF padrão.
# O ProLIF é sensível a formatos, mas é o melhor que existe!