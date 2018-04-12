from flask import Flask
from intweet.webapp.config import SECRET_KEY
from intweet.webapp.routes import bp
import time


webapp = Flask(__name__)
webapp.secret_key = SECRET_KEY
webapp.register_blueprint(bp)


def format_unix_timestamp(dtime):
    return int(time.mktime(dtime.timetuple()))


webapp.jinja_env.filters['unixtime'] = format_unix_timestamp
