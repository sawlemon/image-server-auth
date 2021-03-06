from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_login import login_user, logout_user, login_required
from . import db
import os 

auth = Blueprint('auth', __name__)

def create_size_folder(name, image_size):
    """ returns a subfolder named string to create directory
    >>> create_size_folder('john','small')
    /projects/images/john/small
    """
    return  f'project/images/{name}/{image_size}'

# PAGE ROUTES
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, 
    # and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) 
        # if the user doesn't exist or password is wrong, reload the page
    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    try:
        user = User.query.filter_by(email=email).first() 
    except :
        print('Exception occured')
        user = False
    # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email Already Exists!!')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # TODO : Create a serperate function to handle os works
    user_directory = create_size_folder(name, 'original')
    
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
        os.makedirs(create_size_folder(name, 'small'))
        os.makedirs(create_size_folder(name, 'medium'))
        os.makedirs(create_size_folder(name, 'large'))
    else:
        flash('Email Already Exists!!')
        return redirect(url_for('auth.signup'))
    return redirect(url_for('auth.login'))