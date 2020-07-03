import mysql.connector as con

mycon = con.connect(host="sql12.freesqldatabase.com",user="sql12352288",password="7X35JENbK3",port=3306,database="sql12352288")

mycursor = mycon.cursor()

try:
    mycursor.execute("create table curie (id INT PRIMARY KEY, email VARCHAR(255), receptor VARCHAR(255), ligand VARCHAR(255), config VARCHAR(255), date DATE, description VARCHAR(255),done TINYINT DEFAULT 0)")
except con.ProgrammingError:
    print("Table Already Exists!")

try:
    mycursor.execute("insert into curie values (1,'navanchauhan@gmail.com','lu.pdbqt','test.pdbqt','owo.txt',CURDATE(),'CURIE WEB TASK',0)")
except con.IntegrityError:
    print("Duplicate Entry For Primary Key!")

mycon.commit()