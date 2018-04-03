from flask import Flask
from webapp.config import SECRET_KEY
from flask_bootstrap import Bootstrap

webapp = Flask(__name__, static_url_path='')
webapp.secret_key = SECRET_KEY
Bootstrap(webapp)

from webapp import routes