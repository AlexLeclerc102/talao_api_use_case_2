# export FLASK_APP=demo
# export FLASK_DEBUG=1
from urllib.parse import urlencode
from flask import Blueprint, render_template, request, session, redirect
from . import db
from .models import User
from flask_login import login_required, current_user
import random, json, requests

main = Blueprint('main', __name__)

# Get your own credentials from talao.co !
with open('demo/client_credentials.json') as c:
    credentials = json.load(c)[0]

client_id = credentials["id"]
client_secret = credentials["secret"]

url_callback = "http://127.0.0.1:5000/callback"

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                            name=current_user.name,
                            did = current_user.did,
                            username = current_user.username)

@main.route('/user_list')
@login_required
def user_list():
    user_list = User.query.all()
    return render_template('user_list.html',user_list = user_list)

@main.route('/get_certificate_list', methods=['POST'])
@login_required
def get_certificate_list():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : ''
    }
    # First ask for a token:
    response = requests.post("https://talao.co/api/v1/oauth/token", data=data, auth=(client_id, client_secret))
    print('step 2 : request for a token sent')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 : request sent')
        # Then use it to request the certificate list
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        # You will need to have the did (Decentralized IDentifier) and the type of certificate
        data = {'did' : request.args['did'], 'certificate_type' : request.form['type']}
        response = requests.post('https://talao.co/api/v1/get_certificate_list', data=json.dumps(data), headers=headers)
        response_json = response.json()
        certificate_list = []
        # the response is a list of certificate id you will need to request them if you need the data
        for id in response_json['certificate_list']:
            # get_certificate is used to request the data in the certificate using the certificate id
            # Tokens have a lifetime of 50 minutes, try to reuse them !
            # But don't forget about the token's scope
            certificate = get_certificate(id, token_data)
            if certificate == None:
                return "Error during the request of certificate with id : " + id
            else:
                certificate_list.append(certificate)
        return render_template("show_certificate_list.html", certificate_list = certificate_list)
    return 'Request for a token refused'

def get_certificate(id, token_data):
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : ''
    }
    # Use the token_data passed to request the certificate
    print("requesting certificate with id : " + id)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
    data = {'certificate_id' : id}
    response = requests.post('https://talao.co/api/v1/get_certificate', data=json.dumps(data), headers=headers)
    return response.json()

@main.route('/issue_certificate', methods=['POST'])
@login_required
def issue_certificate():
    if request.form['type'] == "experience":
        return redirect('/issue_experience?did=' + request.args['did'])
    else:
        return "Not implemented"

@main.route('/issue_experience', methods=['GET', 'POST'])
@login_required
def issue_experience():
    if request.method == 'GET' :
        did = request.args['did']
        user = User.query.filter_by(did=did).first()
        return render_template("issue_experience.html", did = user.did, name = user.name)
    if request.method == 'POST' :
        certificate = {
        "title" : request.form['title'],
        "description" : request.form['description'],
        "start_date" : request.form['start_date'],
        "end_date" : request.form['end_date'],
        "skills" : ["Python", "Flask", "Oauth 2.0", "IODC"],
        "score_recommendation" : request.form['score_recommendation'],
        "score_delivery" : request.form['score_delivery'],
        "score_schedule" : request.form['score_schedule'],
        "score_communication" : request.form['score_communication'],
        }
        session['certificate_to_be_issued'] = certificate
        session['did'] = request.form['did']
        session['certificate_type'] = "experience"
        data = {
            'response_type': 'code',
            'client_id': client_id,
            'state': str(random.randint(0, 99999)),
            'nonce' : 'test',
            'redirect_uri': url_callback,
            'scope': 'user:manage:certificate',
        }
        session['state'] = data['state']
        session['endpoint'] = 'user_issues_certificate'
        print('step 1 : demande d autorisation envoyée ')
        return redirect("https://talao.co/api/v1/authorize" + '?' + urlencode(data))


@main.route('/add_referent', methods=['GET'])
@login_required
def add_referent():
    data = {
    'response_type': 'code',
    'client_id': client_id,
    'state': str(random.randint(0, 99999)),
    'nonce' : 'test' + str(random.randint(0, 100)),
    'redirect_uri': url_callback,
    'scope': 'user:manage:referent',
    }
    session['did_referent'] = request.args['did_referent']
    session['state'] = data['state']
    session['endpoint'] = 'user_adds_referent'
    print('step 1 : demande d autorisation envoyée ')
    return redirect( "https://talao.co/api/v1/authorize" + '?' + urlencode(data))

@main.route('/callback')
@login_required
def callback():
    code = request.args.get('code')
    if request.args.get('state') != session['state'] :
        return 'probleme state/CSRF'
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': url_callback,
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'scope' : '' # inutile
    }
    response = requests.post('https://talao.co/api/v1/oauth/token', data=data, auth=(client_id, client_secret))
    print('step 2 : demande d un Access Token envoyée')
    if response.status_code == 200:
        token_data = response.json()
        # appel du endpoint selon la variable state
        params = {'schema': 'oauth2'}
        headers = {'Authorization': 'Bearer %s' % token_data['access_token']}

        if session['endpoint'] == 'user_adds_referent' :
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            data = {'did_referent' : session['did_referent']}
            endpoint_response = requests.post('https://talao.co/api/v1/user_adds_referent', data=json.dumps(data), headers=headers)
            print(endpoint_response.json())
            del session['state']
            del session['endpoint']
            del session['did_referent']
            return "Referent added"
        elif session['endpoint'] == 'user_issues_certificate' :
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            data = {'did_issued_to' : session['did'], 'certificate_type' : session['certificate_type'], 'certificate' : session['certificate_to_be_issued']}
            endpoint_response = requests.post('https://talao.co/api/v1/user_issues_certificate', data=json.dumps(data), headers=headers)
            del session['state']
            del session['endpoint']
            del session['did']
            del session['certificate_type']
            del session['certificate_to_be_issued']
            print(endpoint_response.json())
            try:
                msg = endpoint_response.json()['detail']
            except:
                msg = endpoint_response.json()['link']
            return render_template('certificate_issued.html', msg = msg)
    return 'Probleme de token'
