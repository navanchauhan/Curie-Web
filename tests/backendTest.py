import mysql.connector as con

mycon = con.connect(host="navanspi.duckdns.org",user="curieweb",password="curie-web-russian-54",port=3306,database="curie")
mycursor = mycon.cursor()

# If we are running the CI on an actual server, try using the 6LU7 Mpro and Geraniin Job ID because Eucalyptol fails
sql_select_Query = 'select * from curieweb where id="l9xo2isr98oepcia" LIMIT 1'
mycursor.execute(sql_select_Query)

records = mycursor.fetchall()

def email(zi):
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
    attachment = open((str(zi) + ".zip"), "rb") 
    p = MIMEBase('application', 'octet-stream') 
    p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    msg.attach(p) 
    
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(fromaddr, 'ircd mday avbc tice') 
    
    text = msg.as_string() 
    
    s.sendmail(fromaddr, toaddr, text) 
    s.quit() 

receptor_name = "protein.pdbqt"
ligand_name = "ligand.pdbqt"
description = "GitHub Action Test"

#print(records[0])
r = records[0]
jobID = r[0]
toEmail = r[1]
targetB = r[2]
if r[3] != None:
    receptor_name = str(r[3])
if r[6] != None:
    ligand_name = str(r[6])
ligandB = r[4]
configB = r[7]
date = r[8]
if r[9] != None:
    description = r[9]

import os
cd = os.getcwd()
f = os.path.join(cd,"static/uploads")
#t = os.path.join(f,"receptor",target)
#r = os.path.join(f,"ligands",ligand)
#c = os.path.join(f,"configs",config)
print(f)
import tempfile
from shutil import copy
from shutil import make_archive

with tempfile.TemporaryDirectory() as directory:
    print('The created temporary directory is %s' % directory)
    os.chdir(directory)
#    copy(t,os.getcwd())
#    copy(r,os.getcwd())
#    copy(c, os.getcwd())
    file = open(receptor_name,"wb")
    file.write(targetB)
    file.close()
    file = open(ligand_name,"wb")
    file.write(ligandB)
    file.close()
    file = open("config.txt","wb")
    file.write(configB)
    file.close()
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