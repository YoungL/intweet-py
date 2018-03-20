from flask import Flask
from flask_bootstrap import Bootstrap

webapp = Flask(__name__)
Bootstrap(webapp)

from webapp import routes