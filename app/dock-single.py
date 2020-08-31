import argparse
import logging
import multiprocessing
import os
import sys
from argparse import ArgumentParser
from collections import namedtuple

import mysql.connector as con

mycon = con.connect(host='192.168.1.6',user="curieweb",password="curie-web-russian-54",port=3306,database="curie")
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

def get3DModel(protein,ligand):
	import pymol2
	session = pymol2.PyMOL()
	session.start()
	cmd = session.cmd
	cmd.load(protein,"target")
	cmd.load(ligand,"ligand")
	cmd.save("model.dae")
	session.stop()

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


def email(zipArchive):
    import smtplib 
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText 
    from email.mime.base import MIMEBase 
    from email import encoders 
    
    fromaddr = "navanchauhan@gmail.com"
    
    msg = MIMEMultipart()  
    msg['From'] = fromaddr 
    msg['To'] = toaddr   
    msg['Subject'] = "Curie Web Results for Job ID " + str(jobID)
    body = "Attached Zip contains the docked files, PLIP report and PyMOL Visualisations. If the ZIP file does not contain these files, please report this issue by replying to this email. Job was submitted on {} with the description {}".format(date, description)
    
    msg.attach(MIMEText(body, 'plain')) 
    filename = "Curie_Web_Results_Job_ID_" + str(jobID) + ".zip"
    p = MIMEBase('application', 'octet-stream') 
    with open((str(zipArchive) + ".zip"), "rb") as attachment:
        p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    msg.attach(p) 
    
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(fromaddr, 'okrs shoc ahtk idui') 
    text = msg.as_string() 
    
    s.sendmail(fromaddr, toaddr, text) 
    s.quit() 


inPDB = records[2]
jobID = records[0]
toaddr = records[1]
description = records[5]
date = records[6]

#pdb_file_name = pdbpath.split('/')[-1]
#pdbpath="./6lu7.pdb"

import os
cd = os.getcwd()
f = os.path.join(cd,"static/uploads")
reportDirectory = os.path.join(f,"reports")
modelDirectory = os.path.join(f,"3DModels")
#t = os.path.join(f,"receptor",target)
#r = os.path.join(f,"ligands",ligand)
#c = os.path.join(f,"configs",config)
import tempfile
from shutil import make_archive, copyfile
import time

with tempfile.TemporaryDirectory() as directory:
	print('The created temporary directory is %s' % directory)
	os.chdir(directory)
	pdbpath, pdbid = download_structure(inPDB)
	residues = getResidues(pdbpath)
	selectionResidues = get_select_command(residues,allResidues=False)
	#print(selectionResidues)
	removeWater(pdbpath)
	config = bounding_box(pdbpath,selectionResidues)
	print("Configuration:",config)
	pdbqt = convert_pdb_pdbqt(pdbpath)
	configuration = "size_x={}\nsize_y={}\nsize_z={}\ncenter_x={}\ncenter_y={}\ncenter_z={}".format(config["size_x"],config["size_y"],config["size_z"],config["center_x"],config["center_y"],config["center_z"])
	with open("config.txt","w") as file:
		file.write(configuration)
	os.system('obabel -:"%s" --gen3d -opdbqt -O%s.pdbqt' % (records[3],records[4]))
	os.system("docker run --rm -v ${PWD}:/results -w /results -u $(id -u ${USER}):$(id -g ${USER}) navanchauhan/curie-cli -r %s -l %s -c config.txt -dpi" % (pdbqt,str(records[4]+".pdbqt")))
	z = "Curie_Web_Result_"+str(jobID)
	zi = os.path.join(f,z)
	make_archive(zi, 'zip', directory)
	copyfile("report.pdf",os.path.join(reportDirectory,(str(jobID)+".pdf")))
	get3DModel(pdbpath,"%s_out.pdbqt"%(records[4]))
	os.system("collada2gltf -i model.dae -o model.gltf")
	copyfile("model.gltf",os.path.join(modelDirectory,(str(jobID)+".gltf")))
	os.system("docker run -it --rm -v $(pwd):/usr/app leon/usd-from-gltf:latest model.gltf model.usdz")
	try:
		copyfile("model.usdz",os.path.join(modelDirectory,(str(jobID)+".usdz")))
	except:
		print("Could not generate USDZ file")
	#copy(("Curie_Web_Result_"+str(jobID)),f)
	email(zi)
	#print((str(zi) + ".zip"))
	mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
	mycon.commit()