import flask
from functools import wraps
from flask import Flask, session

try:
    
    from wp1.credentials import ENV, CREDENTIALS
except ImportError:
    print(
        'No credentials.py file found, Please add your credentials in credentials.py'
    )
    ENV = None
    CREDENTIALS = None

 
app = Flask(__name__)

  
app.secret_key = "your_secret_key_here"

  
@app.route('/')
def home():
    return "Flask is running!"

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('user'):
            return f(*args, **kwargs)
        flask.abort(401, 'Unauthorized')
    return wrapper
