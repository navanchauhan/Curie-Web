import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

import configparser
iniConfig = configparser.ConfigParser()
iniConfig.read('config.ini')

try:
    iniConfig['DATABASE']
except KeyError:
    iniConfig.read("../config.ini")


def email(toaddr,jobID,date,description,zipArchive=None,complete=True,reason=None):
    fromaddr = iniConfig['SMTP']['EMAIL']
    
    msg = MIMEMultipart()  
    msg['From'] = fromaddr 
    msg['To'] = toaddr   
    msg['Subject'] = "Curie Web Results for Job ID " + str(jobID)
    if complete:
        body = "Attached Zip contains the docked files, PLIP report and PyMOL Visualisations. If the ZIP file does not contain these files, please report this issue by replying to this email. Job was submitted on {} with the description {}".format(date, description)
    else:
        body = "Task unsuccessful :( \n Job was submitted on {} with the description {}".format(date, description) 

    if reason != None:
        body = reason + str(body)

    msg.attach(MIMEText(body, 'plain'))
    if zipArchive != None:
        filename = "Curie_Web_Results_Job_ID_" + str(jobID) + ".zip"
        p = MIMEBase('application', 'octet-stream') 
        with open((str(zipArchive) + ".zip"), "rb") as attachment:
            p.set_payload((attachment).read()) 
        encoders.encode_base64(p) 
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
        msg.attach(p) 
    
    s = smtplib.SMTP(iniConfig['SMTP']['SERVER'], iniConfig['SMTP']['PORT']) 
    s.starttls() 
    s.login(fromaddr, iniConfig['SMTP']['PASSWORD']) 
    text = msg.as_string() 
    
    s.sendmail(fromaddr, toaddr, text) 
    s.quit() 
