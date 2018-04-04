from flask import Flask
from intweet.webapp.config import SECRET_KEY
from intweet.webapp.routes import bp

webapp = Flask(__name__)
webapp.secret_key = SECRET_KEY
webapp.register_blueprint(bp)
