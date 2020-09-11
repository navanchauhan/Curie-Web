from app import app as flask_app
#app.run(debug=True, host="0.0.0.0", port=8080)
from random import choice, shuffle
from string import digits, ascii_lowercase
from fastapi import Body,FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, escape, request
from pydantic import BaseModel
import os, subprocess


def gen_word(N, min_N_dig, min_N_low):
    choose_from = [digits]*min_N_dig + [ascii_lowercase]*min_N_low
    choose_from.extend([digits + ascii_lowercase] * (N-min_N_low-min_N_dig))
    chars = [choice(bet) for bet in choose_from]
    shuffle(chars)
    return ''.join(chars)

import mysql.connector as con
mycon = con.connect(host=flask_app.config['DB_HOST'],user=flask_app.config['DB_USER'],password=flask_app.config['DB_PASSWORD'],port=flask_app.config['DB_PORT'],database=flask_app.config['DB_NAME'])
mycursor = mycon.cursor()

"""
@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)} from Flask!"
"""

app = FastAPI(title="Curie-API",
    description="API for accessing some of the features.",
    version="0.1",)


@app.get("/v1")
async def API_Version():
    return {"message":"Curie-API v1"}

@app.get("/v1/status/{job_id}")
async def get_status(job_id: str):
    sqlQuery = 'select id, protein_name, ligand_name, date, description, done from curieweb where id="%s"' % (job_id)
    mycursor.execute(sqlQuery)
    records = mycursor.fetchall()
    if records == []:
        return {"message":"Invalid Job ID"}
    r = records[0]
    return {"job_id":r[0],"Protein Name":r[1],"Ligand Name":r[2],"Submitted On":r[3],"Job Description":r[4],"Job Status":r[5]}

@app.get("/v1/3DModels/{job_id}")
async def get_models(job_id: str):
    sqlQuery = 'select done from curieweb where id="%s"' % (job_id)
    mycursor.execute(sqlQuery)
    records = mycursor.fetchall()
    if records == []:
        return {"message":"Invalid Job ID"}
    if records[0][0] == 0:
        return {"message": "The job is still qeued"}
    return {"USDZ":"/static/uploads/3DModels/" + str(job_id) + ".usdz","glTF":"/static/uploads/3DModels/" + str(job_id) + ".gltf"}

@app.get("/v1/Report/{job_id}")
async def get_report(job_id:str):
    sqlQuery = 'select done from curieweb where id="%s"' % (job_id)
    mycursor.execute(sqlQuery)
    records = mycursor.fetchall()
    if records == []:
        return {"message":"Invalid Job ID"}
    if records[0][0] == 0:
        return {"message": "The job is still qeued"}
    return {"PDF Report":"/static/uploads/reports/"+str(job_id)+".pdf"}
   

@app.post("/v1/docking/automatic")
async def docking_automatic(pdb: str, smiles:str,compound_name:str,email:str,description:str):
    if len(pdb) != 0:
        return {"message": "Invalid PDB ID"}
    
    sqlQuery = "insert into curieweb (id, email, pdb, ligand_smile, ligand_name, date, description) values (%s,%s,%s,%s,%s,CURDATE(),%s) "
    jobID = gen_word(16, 1, 1)
    insert_tuple = (jobID,email,pdb,smiles,compound_name,description)
    """
    mycursor.execute(sqlQuery,insert_tuple)
    mycon.commit()
    if flask_app.config['INSTANT_EXEC']:
        cwd = os.path.join(os.getcwd(),"app")
        subprocess.Popen(['python3', 'dock-single.py'],cwd=cwd)
    """

    return {"jobID":jobID,"message":"Sucessfuly Submitted","PDB ID":pdb,"SMILES":smiles,"email":email}
    


app.mount("/", WSGIMiddleware(flask_app))
