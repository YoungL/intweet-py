from webapp import webapp
from webapp.config import *
from flask import render_template

@webapp.route('/')
@webapp.route('/index')
def index():
    # Home Page
    return "Hello, World!"
    
@webapp.route('/login')
def login():
    # Login Page
    local_config = {
        "page_name": "Login"
    }
    return render_template('login.html', global_config=CONFIG, local_config=local_config)

@webapp.route('/register')    
def register():
    # Register Page
    local_config = {
        "page_name": "Register"
    }
    return render_template('register.html', global_config=CONFIG, local_config=local_config)