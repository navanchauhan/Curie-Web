import mysql.connector as con

debug = False
host = "navanspi.duckdns.org"
done = 1

if debug:
    host = "192.168.1.6"
    done = 0

mycon = con.connect(host=host,user="curieweb",password="curie-web-russian-54",port=3306,database="curie")
mycursor = mycon.cursor()

try:
    mycursor.execute("create table curieweb (    id varchar(16) primary key, email nvarchar(255) NOT NULL,   protein LONGBLOB NOT NULL, protein_name VARCHAR(255),  ligand_pdbqt LONGBLOB,   ligand_smile VARCHAR(255),   ligand_name VARCHAR(255),   config LONGBLOB NOT NULL, date DATE, description VARCHAR(255),   done TINYINT DEFAULT 0)")
except con.ProgrammingError:
    print("Table Already Exists!")

from random import choice, shuffle
from string import digits, ascii_lowercase

def gen_word(N, min_N_dig, min_N_low):
    choose_from = [digits]*min_N_dig + [ascii_lowercase]*min_N_low
    choose_from.extend([digits + ascii_lowercase] * (N-min_N_low-min_N_dig))
    chars = [choice(bet) for bet in choose_from]
    shuffle(chars)
    return ''.join(chars)

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

jobID = gen_word(16, 1, 1)
print("Succesfuly submitted Job ID:",jobID)

insert_tuple = (jobID,"b5bmf.{curie-gh-ci}@inbox.testmail.app",receptor,receptorName,ligand,ligandName,config,done)

try:
    mycursor.execute(sqlQuery,insert_tuple)
except con.IntegrityError:
    print("Oops, Collision occured. Generating new Job ID and trying again.")
    jobID = gen_word(16, 1, 1)
    insert_tuple = (jobID,"b5bmf.{curie-gh-ci}@inbox.testmail.app",receptor,receptorName,ligand,ligandName,config,done)
    mycursor.execute(sqlQuery,insert_tuple)

print("Removing Test Query")

q = 'delete from curieweb where id="%s"' % (jobID)
mycursor.execute(q)

mycon.commit()

print("Database working perfectly")
