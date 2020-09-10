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

print("Removing Test Query")
jobID = "l9xo2isr98oepcia"
q = 'delete from curieweb where id="%s"' % (jobID)
mycursor.execute(q)
mycon.commit()

print("Database working perfectly")