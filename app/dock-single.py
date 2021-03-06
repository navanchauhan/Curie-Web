import argparse
import logging
import multiprocessing
import os
import sys
from argparse import ArgumentParser
from collections import namedtuple
import mysql.connector as con
from misc.common import get3DModel, CopyContentOfFolder, RemoveAllFilesMatching
from misc.email import email
from misc.config import iniConfig

mycon = con.connect(host=iniConfig['DATABASE']['HOST'],user=iniConfig['DATABASE']['USER'],password=iniConfig['DATABASE']['PASSWORD'],port=iniConfig['DATABASE']['PORT'],database=iniConfig['DATABASE']['NAME'])
mycursor = mycon.cursor()

sql_select_Query = "SELECT id,email,pdb,ligand_smile,ligand_name,description,date FROM curieweb WHERE pdb IS NOT NULL AND done=0 LIMIT 1"
mycursor.execute(sql_select_Query)

records = mycursor.fetchall()
if records == []:
    print("Empty Set 😳")
    print("No active task, exitting gracefully")
    exit(0)

records = records[0]



print("Importing PLIP..",end="")

from plip.basic import config, logger
from plip.basic.config import __version__
from plip.basic.parallel import parallel_fn
from plip.basic.remote import VisualizerData
from plip.exchange.webservices import fetch_pdb
from plip.structure.preparation import create_folder_if_not_exists, extract_pdbid
from plip.structure.preparation import tilde_expansion, PDBComplex

print(".Done")

def download_structure(inputpdbid):
    """Given a PDB ID, downloads the corresponding PDB structure.
    Checks for validity of ID and handles error while downloading.
    Returns the path of the downloaded file."""
    try:
        if len(inputpdbid) != 4 or extract_pdbid(inputpdbid.lower()) == 'UnknownProtein':
            logger.error(f'invalid PDB-ID (wrong format): {inputpdbid}')
            sys.exit(1)
        pdbfile, pdbid = fetch_pdb(inputpdbid.lower())
        pdbpath = tilde_expansion('%s/%s.pdb' % (config.BASEPATH.rstrip('/'), pdbid))
        create_folder_if_not_exists(config.BASEPATH)
        with open(pdbpath, 'w') as g:
            g.write(pdbfile)
        return pdbpath, pdbid
    except ValueError:  # Invalid PDB ID, cannot fetch from RCBS server
        logger.error(f'PDB-ID does not exist: {inputpdbid}')
        sys.exit(1)

def bounding_box(receptor, residues):
    try:
        import pymol2
    except ImportError:
        raise ImportError("Failed to import PyMOL")
    
    session = pymol2.PyMOL()
    session.start()

    cmd = session.cmd
    cmd.load(pdbpath,"target")
    cmd.select("box",(selectionResidues))

    extent = 5

    ([minX, minY, minZ],[maxX, maxY, maxZ]) = cmd.get_extent("box")

    minX = minX - float(extent)
    minY = minY - float(extent)
    minZ = minZ - float(extent)
    maxX = maxX + float(extent)
    maxY = maxY + float(extent)
    maxZ = maxZ + float(extent)

    SizeX = maxX - minX
    SizeY = maxY - minY
    SizeZ = maxZ - minZ
    CenterX =  (maxX + minX)/2
    CenterY =  (maxY + minY)/2
    CenterZ =  (maxZ + minZ)/2

    session.stop()
    
    return {"size_x": SizeX, "size_y": SizeY, "size_z": SizeZ, "center_x": CenterX, "center_y": CenterY, "center_z": CenterZ}


def removeWater(pdbpath):
	import pymol2
	session = pymol2.PyMOL()
	session.start()
	cmd = session.cmd
	cmd.load(pdbpath,"target")
	cmd.remove('resn HOH')
	cmd.save(pdbpath,"target")
	session.stop()

def getResidues(pdbpath):
	mol = PDBComplex()
	mol.load_pdb(pdbpath)
	for ligand in mol.ligands:
		mol.characterize_complex(ligand)
	
	residues = []
	
	for x in range(len(mol.interaction_sets)):
		if len(mol.interaction_sets[list(mol.interaction_sets.keys())[x]].interacting_res) != 0:
			residues.append(mol.interaction_sets[list(mol.interaction_sets.keys())[x]].interacting_res)

	print(residues)
	return residues

def get_select_command(residues,allResidues=False):
	residues.sort(key=len,reverse=True)
	selectionResidues = ""
	allRes = []
	if len(residues) == 0:
		#print("what the frick, no interacting ligands???")
		print("We could not find any binding sites within the structure.")
	else:
		for x in residues:
			selectionResidues = ""
			for y in x:
				selectionResidues += 'resi ' + y.replace("A","") + ' + '
			allRes.append(selectionResidues.strip()[:-1].strip())

	if allResidues == False:
		return allRes[0]
	return allRes

def convert_pdb_pdbqt(pdbpath):
	import oddt
	from oddt.docking.AutodockVina import write_vina_pdbqt
	print(pdbpath)
	try:
		receptor = next(oddt.toolkit.readfile("pdb",pdbpath.split("./")[1]))
		"""
		# remove zero order bonds from metals
		for atom in receptor: 
			if atom.atomicnum == 30:  # Atomic num of treated metals
				for bond in atom.bonds:
					print("del")
					receptor.OBMol.DeleteBond(bond.OBBond)
		"""
		receptor.calccharges()
	except Exception:
		print("Molecule failed to charge, falling back to RDKit") 
		receptor = next(oddt.toolkits.rdk.readfile("pdb",pdbpath.split("./")[1]))
		receptor.calccharges()

	path = write_vina_pdbqt(receptor,'./',flexible=False)
	return path


inPDB = records[2]
jobID = records[0]
toaddr = records[1]
description = records[5]
date = records[6]


cd = os.getcwd()
print("Curie-Web Directory is:",cd)
f = os.path.join(cd,"static/uploads")
scripts = os.path.join(cd,"scripts")
reportDirectory = os.path.join(f,"reports")
modelDirectory = os.path.join(f,"3DModels")
import tempfile
from shutil import make_archive, copyfile,copy
import time



with tempfile.TemporaryDirectory() as directory:
	print('The created temporary directory is %s' % directory)
	os.chdir(directory)
	
	try:
		pdbpath, pdbid = download_structure(inPDB)
	except:
		reason = "Could not download PDB with the id " + str(inPDB) + ". "
		email(toaddr,jobID,date,description,reason=reason)
		mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
		mycon.commit()
		sys.exit(0)	

	residues = getResidues(pdbpath)
	
	try:
		selectionResidues = get_select_command(residues,allResidues=False)
	except IndexError:
		reason = "Could not find binding site automatically. "
		email(toaddr,jobID,date,description,reason=reason)
		mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
		mycon.commit()
		sys.exit(0)	
	#print(selectionResidues)
	removeWater(pdbpath)
	config = bounding_box(pdbpath,selectionResidues)
	print("Configuration:",config)
	pdbqt = convert_pdb_pdbqt(pdbpath)
	configuration = "size_x={}\nsize_y={}\nsize_z={}\ncenter_x={}\ncenter_y={}\ncenter_z={}".format(config["size_x"],config["size_y"],config["size_z"],config["center_x"],config["center_y"],config["center_z"])
	with open("config.txt","w") as file:
		file.write(configuration)
	os.system('obabel -:"%s" --gen3d -opdbqt -O%s.pdbqt' % (records[3],records[4]))
	print("Ligand:",records[4])
	print(str(records[4]+".pdbqt"))
	CopyContentOfFolder(scripts,directory)
	os.system("./main.sh -r %s -l %s -c config.txt -dpi" % (pdbqt,str(records[4]+".pdbqt")))
	#os.system("docker run --rm -v ${PWD}:/results -w /results -u $(id -u ${USER}):$(id -g ${USER}) navanchauhan/curie-cli -r %s -l %s -c config.txt -dpi" % (pdbqt,str(records[4]+".pdbqt")))
	RemoveAllFilesMatching(directory,".py")
	RemoveAllFilesMatching(directory,".sh")
	z = "Curie_Web_Result_"+str(jobID)
	zi = os.path.join(f,z)
	make_archive(zi, 'zip', directory)
	try:
		copyfile("report.pdf",os.path.join(reportDirectory,(str(jobID)+".pdf")))
	except FileNotFoundError:
		reason = "Could not generate the PDF report, this could be because of a failed docking job. Please check the ZIP archive for the configuration and converted PDBQTs and try submitting manually. "
		email(toaddr,jobID,date,description,zipArchive=zi,reason=reason)
		mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
		mycon.commit()
		sys.exit(0)	
	"""
	try:
		get3DModel(pdbpath,"%s_out.pdbqt"%(records[4]))
	except:
		email(toaddr,jobID,date,description,zipArchive=zi)
		mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
		mycon.commit()
		sys.exit(0)	 
	"""
	get3DModel(pdbpath,"%s_out.pdbqt"%(records[4]))
	os.system("collada2gltf -i model.dae -o model.gltf")
	copyfile("model.gltf",os.path.join(modelDirectory,(str(jobID)+".gltf")))
	arch = os.popen("uname -m").read()
	print("Generating 3D Model")
	if "x86" in arch:
		os.system("docker run --rm -v $(pwd):/usr/app leon/usd-from-gltf:latest model.gltf model.usdz")
	elif "aarch64" in arch:
		os.system("docker run --rm -v $(pwd):/usr/app navanchauhan/usd-from-gltf:latest model.gltf model.usdz")
	try:
		copyfile("model.usdz",os.path.join(modelDirectory,(str(jobID)+".usdz")))
	except:
		print("Could not generate USDZ file")
	email(toaddr,jobID,date,description,zipArchive=zi)
	mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
	mycon.commit()