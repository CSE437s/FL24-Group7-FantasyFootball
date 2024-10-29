from flask import Flask
from os import urandom

def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)
    return app