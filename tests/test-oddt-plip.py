from plip.basic import config
from plip.exchange.webservices import fetch_pdb
from plip.structure.preparation import create_folder_if_not_exists, extract_pdbid
from plip.structure.preparation import tilde_expansion, PDBComplex

pdbId = "6LU7"
print("Downloading PDB:",pdbId)

pdbfile, pdbid = fetch_pdb(pdbId.lower())

pdbpath = tilde_expansion('%s/%s.pdb' % (config.BASEPATH.rstrip('/'), pdbid))
create_folder_if_not_exists(config.BASEPATH)
with open(pdbpath, 'w') as g:
    g.write(pdbfile)

print("Adding Charges")
import oddt
from oddt.docking.AutodockVina import write_vina_pdbqt
receptor = next(oddt.toolkit.readfile("pdb",pdbpath.split("./")[1]))
receptor.calccharges()
#receptor = next(oddt.toolkits.rdk.readfile("pdb",pdbpath.split("./")[1]))
#receptor.calccharges()

print("Writing PDBQT")
path = write_vina_pdbqt(receptor,'.',flexible=False)

smiles = 'CCC(CC)COC(=O)C(C)NP(=O)(OCC1C(C(C(O1)(C#N)C2=CC=C3N2N=CN=C3N)O)O)OC4=CC=CC=C4'

print("Generating Strucutre")
mol = oddt.toolkit.readstring('smi', smiles)
mol.make3D()
print("Adding Charges")
mol.calccharges()

path2 = write_vina_pdbqt(mol,'.',flexible=False)