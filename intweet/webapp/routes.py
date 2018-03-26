from webapp import webapp
from webapp.config import *
from models.user import User
from flask import render_template, request, url_for, session, flash, redirect
from database import get_db_session
from crypt import crypt
from sqlalchemy import exc
from sqlalchemy.dialects import mysql


@webapp.route('/')
@webapp.route('/home')
def home():
    local_config = {
        "page_name": "Home"
    }
    # Home Page
    if session.get('logged_in'):
        userdata = {
            'fullname': session.get('name'),
            'email': session.get('email')
        }
        return render_template('user_home.html', global_config=CONFIG, 
            local_config=local_config, userdata=userdata)
    else:
        return render_template('home.html', global_config=CONFIG, 
            local_config=local_config)
            
@webapp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('home'))
    
@webapp.route('/login', methods=['GET', 'POST'])
def login():
    # Login Page
    error = {}
    error['errors'] = 0
    if request.method == 'POST':
        if not request.form['email'] or len(request.form['email']) == 0:
            error['message'] = "No email address provided"
            error['errors'] += 1
            
        elif not request.form['password'] or len(request.form['password']) == 0:
            error['message'] = "No password provided"
            error['errors'] += 1
        
        else:
            # Attempt to log the user in
            db = get_db_session()
            query = db.query(User).\
                filter(User.email == request.form['email'])
            user = query.one()
            if not user.validate_password(request.form['password']):
                # email and password incorrect
                error['message'] = "Invalid credentials"
                error['errors']  += 1
            else:
                # email and password correct - log the user in!
                session['logged_in'] = True
                session['user'] = user.email
                session['name'] = user.fullname
                return redirect(url_for('home'))
                

    local_config = {
        "page_name": "Login"
    }
    return render_template('login.html', global_config=CONFIG, 
        local_config=local_config, error=error)

@webapp.route('/register')    
def register():
    # Register Page
    local_config = {
        "page_name": "Register"
    }
    return render_template('register.html', global_config=CONFIG, local_config=local_config)