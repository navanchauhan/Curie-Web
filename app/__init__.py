from flask import Flask

# Config Values
# location where file uploads will be stored
UPLOAD_FOLDER = './app/static/uploads'
DB_HOST = '192.168.1.6' #'navanspi.duckdns.org'
DB_PORT = 3306
DB_USER = 'curieweb'
DB_PASSWORD = 'curie-web-russian-54'
DB_NAME = 'curie'
# needed for session security, the flash() method in this case stores the message
# in a session
SECRET_KEY = 'Sup3r$3cretkey'

app = Flask(__name__)
app.config.from_object(__name__)

from app import views