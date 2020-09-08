import mysql.connector as con

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

try:
    config['DATABASE']
except KeyError:
    config.read("../config.ini")

mycon = con.connect(host=config['DATABASE']['HOST'],user=config['DATABASE']['USER'],password=config['DATABASE']['PASSWORD'],port=config['DATABASE']['PORT'],database=config['DATABASE']['NAME'])
mycursor = mycon.cursor()

sql_select_Query = "select * from curieweb where done=0 LIMIT 1"
mycursor.execute(sql_select_Query)

records = mycursor.fetchall()
if records == []:
    print("Empty Set 😳")
    print("No active task, exitting gracefully")
    exit(0)

def email(zipArchive):
    import smtplib 
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText 
    from email.mime.base import MIMEBase 
    from email import encoders 
    
    fromaddr = "navanchauhan@gmail.com"
    toaddr = toEmail
    
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

def get3DModel(protein,ligand):
    try:
        import pymol2
    except ImportError:
        print("🤭 PyMOL 2 has not been installed correctly")
        return None
    session = pymol2.PyMOL()
    session.start()
    cmd = session.cmd
    cmd.load(protein,"target")
    cmd.load(ligand,"ligand")
    cmd.save("model.dae")
    session.stop()

receptor_name = "protein.pdbqt"
ligand_name = "ligand.pdbqt"
description = "Curie Web Task"

#print(records[0])
r = records[0]
jobID = r[0]
toEmail = r[1]
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

import os
cd = os.getcwd()
f = os.path.join(cd,"static/uploads")
reportDirectory = os.path.join(f,"reports")
modelDirectory = os.path.join(f,"3DModels")
#t = os.path.join(f,"receptor",target)
#r = os.path.join(f,"ligands",ligand)
#c = os.path.join(f,"configs",config)
print(f)
import tempfile
from shutil import make_archive, copyfile

with tempfile.TemporaryDirectory() as directory:
    print('The created temporary directory is %s' % directory)
    os.chdir(directory)
#    copy(t,os.getcwd())
#    copy(r,os.getcwd())
#    copy(c, os.getcwd())
    with open(receptor_name,"wb") as file:
        file.write(targetB)
    with open(ligand_name,"wb") as file:
        file.write(ligandB)
    with open("config.txt","wb") as file:
        file.write(configB)
    os.system("docker run --rm -v ${PWD}:/results -w /results -u $(id -u ${USER}):$(id -g ${USER}) navanchauhan/curie-cli -r %s -l %s  -c config.txt -dpi" % (receptor_name,ligand_name))
    #copy("report.pdf",f)
    z = "Curie_Web_Result_"+str(jobID)
    zi = os.path.join(f,z)
    make_archive(zi, 'zip', directory)
    #copy(("Curie_Web_Result_"+str(jobID)),f)
    copyfile("report.pdf",os.path.join(reportDirectory,(str(jobID)+".pdf")))
    get3DModel(receptor_name,ligand_name.replace(".pdbqt","_out.pdbqt"))
    os.system("collada2gltf -i model.dae -o model.gltf")
    copyfile("model.gltf",os.path.join(modelDirectory,(str(jobID)+".gltf")))
    arch = os.popen("uname -m").read()
    if "x86" in arch:
        os.system("docker run -it --rm -v $(pwd):/usr/app leon/usd-from-gltf:latest model.gltf model.usdz")
    elif "aarch64" in arch:
        os.system("docker run -it --rm -v $(pwd):/usr/app navanchauhan/usd-from-gltf:latest model.gltf model.usdz")
    try:
        copyfile("model.usdz",os.path.join(modelDirectory,(str(jobID)+".usdz")))
    except:
        print("Could not generate USDZ file")
    email(zi)
    #print((str(zi) + ".zip"))
    mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
    mycon.commit()    
