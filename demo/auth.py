from flask import Blueprint, render_template , redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db
import json, requests

auth = Blueprint('auth', __name__)

# Get your own credentials from talao.co !
with open('demo/client_credentials.json') as c:
    credentials = json.load(c)[0]

client_id = credentials["id"]
client_secret = credentials["secret"]

# Usefull url
talao_url = " https://talao.co"
# Talao as an OAuth2 Identity Provider
talao_url_token = talao_url + '/api/v1/oauth/token'

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
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    response = create_Talao_company(name, email)
    try:
        username, did = response['username'], response['did']
    except:
        flash('Problem with the Talao API, please contact admin')
        return redirect(url_for('auth.signup'))
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name,
                    username=username, did= did,
                    password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))

def create_Talao_company(name, email):
    data = {
            'grant_type': 'client_credentials',
            'redirect_uri': "",
            'client_id': client_id,
            'client_secret': client_secret,
            'code': "",
            'scope' : 'client:create:identity' # You will need to have this scope allowed by talao.co
        }
    # First ask for a token:
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 1 : request for a token sent')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 2 : request sent')
        #T hen use it to request the creation of a new identity:
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'name' : name, 'email' : email, "send_email" : True}
        # If send_email is True we will send an email to the user to invite him on our platform (talao.co)
        # where he will have acces to all our services
        # Send the request:
        response = requests.post(talao_url + '/api/v1/create_company_identity', data=json.dumps(data), headers=headers)
        print('step 3 : response received')
        return response.json()

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
