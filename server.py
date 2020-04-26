from os import environ
from flask import Flaskapp = Flask(__name__)


app.run(host= '0.0.0.0', port=environ.get('PORT'))
