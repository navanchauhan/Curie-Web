import mysql.connector as con
from app import app

mycon = con.connect(host=app.config['DB_HOST'],user="curieweb",password="curie-web-russian-54",port=3306,database="curie")
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
#t = os.path.join(f,"receptor",target)
#r = os.path.join(f,"ligands",ligand)
#c = os.path.join(f,"configs",config)
print(f)
import tempfile
from shutil import make_archive

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
    email(zi)
    #print((str(zi) + ".zip"))
    mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
    mycon.commit()    
