from app import app as flask_app
#app.run(debug=True, host="0.0.0.0", port=8080)

from fastapi import Body,FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, escape, request
from pydantic import BaseModel

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
    description="API for accessing most of the features.",
    version="0.1",)


@app.get("/v1")
def API_Version():
    return {"message":"Curie-API v1"}
    


@app.get("/v1/status/{job_id}")
def get_status(job_id: str):
    sqlQuery = 'select id, protein_name, ligand_name, date, description, done from curieweb where id="%s"' % (job_id)
    mycursor.execute(sqlQuery)
    records = mycursor.fetchall()
    if records == []:
        return {"message":"Invalid Job ID"}
    r = records[0]
    return {"job_id":r[0],"Protein Name":r[1],"Ligand Name":r[2],"Submitted On":r[3],"Job Description":r[4],"Job Status":r[5]}


app.mount("/", WSGIMiddleware(flask_app))
