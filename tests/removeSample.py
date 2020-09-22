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

print("Removing Test Query")
jobID = "l9xo2isr98oepcia"
q = 'delete from curieweb where id="%s"' % (jobID)
mycursor.execute(q)
mycon.commit()

print("Database working perfectly")