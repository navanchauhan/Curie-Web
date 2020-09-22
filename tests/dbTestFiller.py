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
    emailPort = returnValue("CURIE_EMAIL_PORT")
    emailPassword = returnValue("CURIE_EMAIL_PASSWORD")
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
done = 1

try:
    mycursor.execute("create table curieweb (    id varchar(16) primary key, email nvarchar(255) NOT NULL,   protein LONGBLOB NOT NULL, protein_name VARCHAR(255),  ligand_pdbqt LONGBLOB,   ligand_smile VARCHAR(255),   ligand_name VARCHAR(255),   config LONGBLOB NOT NULL, date DATE, description VARCHAR(255),   done TINYINT DEFAULT 0, pdb VARCHAR(4),csv longblob)")
except con.ProgrammingError:
    print("Table Already Exists!")

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

ligand = convertToBinaryData("./files/Eucalyptol.pdbqt")
receptor = convertToBinaryData("./files/6LU7.pdbqt")
config = convertToBinaryData("./files/6LU7.txt")
ligandName = "Eucalyptol"
receptorName = "6LU7"
sqlQuery = "insert into curieweb (id, email, protein, protein_name, ligand_pdbqt, ligand_name,date, config,done) values (%s,%s,%s,%s,%s,%s,CURDATE(),%s,%s) "
jobID = "l9xo2isr98oepcia"

insert_tuple = (jobID,"b5bmf.{curie-gh-ci}@inbox.testmail.app",receptor,receptorName,ligand,ligandName,config,done)
mycursor.execute(sqlQuery,insert_tuple)
print("Succesfuly submitted Job ID:",jobID)


mycon.commit()
