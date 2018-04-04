from flask import Flask
from intweet.webapp.config import SECRET_KEY
from flask_bootstrap import Bootstrap

webapp = Flask(__name__, static_url_path='')
webapp.secret_key = SECRET_KEY
Bootstrap(webapp)

from intweet.webapp import routes