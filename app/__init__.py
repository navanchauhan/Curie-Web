from flask import Flask

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

DB_HOST = config['DATABASE']['HOST']
DB_PORT = config['DATABASE']['PORT']
DB_USER = config['DATABASE']['USER']
DB_PASSWORD = config['DATABASE']['PASSWORD']
DB_NAME = config['DATABASE']['NAME']
LOG_FOLDER = config['FILES']['LOG_FOLDER']
INSTANT_EXEC = config['EXECUTION']['INSTANT']
LSTM = config['FEATURES']['LSTM']

if LSTM == 'True':
    LSTM = True
else:
    LSTM = False

if INSTANT_EXEC == 'True':
    INSTANT_EXEC = True
else:
    INSTANT_EXEC = False

LOG = True
SAVE_LOGS = False

if config['LOGS']['LOG'] == 'True':
    LOG = True
    if config['LOGS']['SAVE_LOGS'] == 'True':
        SAVE_LOGS = True
else:
    LOG = False

"""
# Hardcoded Values
# location where file uploads will be stored
UPLOAD_FOLDER = './app/static/uploads'
DB_HOST = 'navanspi.duckdns.org' #'navanspi.duckdns.org'
DB_PORT = 3306
DB_USER = 'curieweb'
DB_PASSWORD = 'curie-web-russian-54'
DB_NAME = 'curie'


import subprocess
import hashlib
ssid = b'j\xa0\x1b\xd6p\xe9\xa4\\b\x12\xedD\xaeX\x8a\xf8'

try:
    output = subprocess.check_output(['iwgetid'])
    if hashlib.md5(bytes(output.decode().split('"')[1],encoding="utf-8")).digest() == ssid:
        DB_HOST = '192.168.1.6'
except:
    None
"""

# needed for session security, the flash() method in this case stores the message
# in a session
SECRET_KEY = 'Sup3r$3cretkey'

app = Flask(__name__)
#app = Flask(__name__, static_url_path='static')
app.config.from_object(__name__)

from app import views