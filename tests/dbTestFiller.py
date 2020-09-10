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
done = 1

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
