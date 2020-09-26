import mysql.connector as con
from misc.common import get3DModel, CopyContentOfFolder, RemoveAllFilesMatching
from misc.email import email
import os
import configparser
import sys

iniConfig = configparser.ConfigParser()
iniConfig.read('config.ini')

try:
    iniConfig['DATABASE']
except KeyError:
    iniConfig.read("../config.ini")

mycon = con.connect(host=iniConfig['DATABASE']['HOST'],user=iniConfig['DATABASE']['USER'],password=iniConfig['DATABASE']['PASSWORD'],port=iniConfig['DATABASE']['PORT'],database=iniConfig['DATABASE']['NAME'])
mycursor = mycon.cursor()

sql_select_Query = "select * from curieweb where done=0 LIMIT 1"
mycursor.execute(sql_select_Query)

records = mycursor.fetchall()
if records == []:
    print("Empty Set 😳")
    print("No active task, exitting gracefully")
    exit(0)

receptor_name = "protein.pdbqt"
ligand_name = "ligand.pdbqt"
description = "Curie Web Task"

#print(records[0])
r = records[0]
jobID = r[0]
toEmail = r[1]
toaddr = toEmail
targetB = r[2]
if r[3] is not None:
    receptor_name = str(r[3])
if r[6] is not None:
    ligand_name = str(r[6])
ligandB = r[4]
configB = r[7]
date = r[8]
if r[9] is not None:
    description = r[9]
else:
    description = "not specified"

cd = os.getcwd()
f = os.path.join(cd,"static/uploads")
reportDirectory = os.path.join(f,"reports")
scripts = os.path.join(cd,"scripts")
modelDirectory = os.path.join(f,"3DModels")

import tempfile
from shutil import make_archive, copyfile,copy

with tempfile.TemporaryDirectory() as directory:
    print('The created temporary directory is %s' % directory)
    os.chdir(directory)
    with open(receptor_name,"wb") as file:
        file.write(targetB)
    with open(ligand_name,"wb") as file:
        file.write(ligandB)
    with open("config.txt","wb") as file:
        file.write(configB)
    # Legacy Docker Curie-Cli Run
    #os.system("docker run --rm -v ${PWD}:/results -w /results -u $(id -u ${USER}):$(id -g ${USER}) navanchauhan/curie-cli -r %s -l %s  -c config.txt -dpi" % (receptor_name,ligand_name))
    CopyContentOfFolder(scripts,directory)
    os.system("./main.sh -r %s -l %s -c config.txt -dpi" % (receptor_name,ligand_name))
    RemoveAllFilesMatching(directory,".py")
    RemoveAllFilesMatching(directory,".sh")
    z = "Curie_Web_Result_"+str(jobID)
    zi = os.path.join(f,z)
    make_archive(zi, 'zip', directory)
    try:
        copyfile("report.pdf",os.path.join(reportDirectory,(str(jobID)+".pdf")))
    except:
        reason = "Could not generate the report, this could be because of a failed docking job. Please check the ZIP archive for the configuration and converted PDBQTs and try submitting manually. "
        email(toaddr,jobID,date,description,zipArchive=zi,reason=reason)
        mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
        mycon.commit()
        sys.exit(0)	
    res = get3DModel(receptor_name,ligand_name.replace(".pdbqt","_out.pdbqt"))
    if res == None:
        reason = "Could not generate the 3D models."
        email(toaddr,jobID,date,description,zipArchive=zi)
        mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
        mycon.commit()
        sys.exit(0)	 
    os.system("collada2gltf -i model.dae -o model.gltf")
    try:
        copyfile("model.gltf",os.path.join(modelDirectory,(str(jobID)+".gltf")))
    except:
        print("Does not have Collada2GLTF Installed")
        email(toaddr,jobID,date,description,zipArchive=zi)
        mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
        mycon.commit()
        exit(0)
    arch = os.popen("uname -m").read()
    print("Generating 3D Model")
    if "x86" in arch:
        os.system("docker run -it --rm -v $(pwd):/usr/app leon/usd-from-gltf:latest model.gltf model.usdz")
    elif "aarch64" in arch:
        os.system("docker run -it --rm -v $(pwd):/usr/app navanchauhan/usd-from-gltf:latest model.gltf model.usdz")
    try:
        copyfile("model.usdz",os.path.join(modelDirectory,(str(jobID)+".usdz")))
    except:
        print("Could not generate USDZ file")
    email(toaddr,jobID,date,description,zipArchive=zi)
    mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
    mycon.commit()    
