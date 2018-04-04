from flask import Flask
from intweet.webapp.config import SECRET_KEY

webapp = Flask(__name__, static_url_path='')
webapp.secret_key = SECRET_KEY

from intweet.webapp import routes