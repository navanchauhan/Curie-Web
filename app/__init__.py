from flask import Flask

# Config Values
# location where file uploads will be stored
UPLOAD_FOLDER = './app/static/uploads'
DB_HOST = 'navanspi.duckdns.org' #'navanspi.duckdns.org'

import subprocess
import hashlib
ssid = b'j\xa0\x1b\xd6p\xe9\xa4\\b\x12\xedD\xaeX\x8a\xf8'

try:
    output = subprocess.check_output(['iwgetid'])
    if hashlib.md5(bytes(output.decode().split('"')[1],encoding="utf-8")).digest() == ssid:
        DB_HOST = '192.168.1.6'
except:
    None

DB_PORT = 3306
DB_USER = 'curieweb'
DB_PASSWORD = 'curie-web-russian-54'
DB_NAME = 'curie'
# needed for session security, the flash() method in this case stores the message
# in a session
SECRET_KEY = 'Sup3r$3cretkey'

app = Flask(__name__)
#app = Flask(__name__, static_url_path='static')
app.config.from_object(__name__)

from app import views