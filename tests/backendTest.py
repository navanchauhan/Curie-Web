import os
import mysql.connector as con
from mysql.connector.errors import InterfaceError

GitHubWorkflow = True

try:
    print(os.environ['GITHUB_ACTIONS'])
except:
    GitHubWorkflow = False

def returnValue(key):
    return os.environ[key]

if GitHubWorkflow:
    host = returnValue("CURIE_HOST")
    db = returnValue("CURIE_DB")
    user = returnValue("CURIE_USER")
    port = returnValue("CURIE_PORT")
    password = returnValue("CURIE_PASSWORD")
    fromaddr = returnValue("CURIE_EMAIL")
    emailServer = returnValue("CURIE_EMAIL_SERVER")
    emailPort = returnValye("CURIE_EMAIL_PORT")
    emailPassword = returnValye("CURIE_EMAIL_PASSWORD")
else:
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        config['DATABASE']
    except KeyError:
        config.read("../config.ini")
    v = config['DATABASE']

    host = v['HOST']
    db = v['NAME']
    user = v['USER']
    password = v['PASSWORD']
    port = v['PORT']
    fromaddr = config['SMTP']['EMAIL']
    emailServer = config['SMTP']['SERVER']
    emailPort = config['SMTP']['PORT'] 
    emailPassword = config['SMTP']['PASSWORD'] 


try:
    mycon = con.connect(host=host,user=user,password=password,port=port,database=db)
except InterfaceError:
    print("Could not connect to the database")
    sys.exit(1)
mycursor = mycon.cursor()

# If we are running the CI on an actual server, try using the 6LU7 Mpro and Geraniin Job ID because Eucalyptol fails
sql_select_Query = 'select * from curieweb where id="l9xo2isr98oepcia" LIMIT 1'
mycursor.execute(sql_select_Query)

records = mycursor.fetchall()

def email(compressedFile):
    import smtplib 
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText 
    from email.mime.base import MIMEBase 
    from email import encoders 
    
    fromaddr = fromaddr
    toaddr = toEmail
    
    msg = MIMEMultipart()  
    msg['From'] = fromaddr 
    msg['To'] = toaddr   
    msg['Subject'] = "Curie Web Results for Job ID " + str(jobID)
    body = "Attached Zip contains the docked files, PLIP report and PyMOL Visualisations. If the ZIP file does not contain these files, please report this issue by replying to this email. Job was submitted on {} with the description {}".format(date, description)
    
    msg.attach(MIMEText(body, 'plain')) 
    filename = "Curie_Web_Results_Job_ID_" + str(jobID) + ".zip"
    p = MIMEBase('application', 'octet-stream') 
    with open((str(compressedFile) + ".zip"), "rb") as attachment:
        p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    msg.attach(p) 
    
    s = smtplib.SMTP(emailServer, emailPort) 
    s.starttls() 
    s.login(fromaddr, emailPassword) 
    
    text = msg.as_string() 
    
    s.sendmail(fromaddr, toaddr, text) 
    s.quit() 

receptor_name = "protein.pdbqt"
ligand_name = "ligand.pdbqt"
description = "Test"

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

if ".pdbqt" not in receptor_name:
    receptor_name+=".pdbqt"

if ".pdbqt" not in ligand_name:
    ligand_name+=".pdbqt"

print(f)
import tempfile
from shutil import make_archive

with tempfile.TemporaryDirectory() as directory:
    print('The created temporary directory is %s' % directory)
    os.chdir(directory)
    with open(receptor_name,"wb") as file:
        file.write(targetB)
    with open(ligand_name,"wb") as file:
        file.write(ligandB)
    with open("config.txt","wb") as file:
        file.write(configB)
    os.system("docker run --rm -v ${PWD}:/results -w /results -u $(id -u ${USER}):$(id -g ${USER}) navanchauhan/curie-cli -r %s -l %s  -c config.txt -dpi" % (receptor_name,ligand_name))
    z = "Curie_Web_Result_"+str(jobID)
    zi = os.path.join(f,z)
    make_archive(zi, 'zip', directory)
    email(zi)
    mycursor.execute('UPDATE curieweb set done=1 where id="%s"' % (jobID))
    mycon.commit()    

