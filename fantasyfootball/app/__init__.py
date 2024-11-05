# app/__init__.py

from flask import Flask, g
from os import urandom
from dotenv import load_dotenv
from .db import create_access_tokens_table, get_access_token
from .routes import api, main


def create_app():
    load_dotenv(override=True)

    app = Flask(__name__)
    app.secret_key = urandom(24)

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(main)

    create_access_tokens_table()

    @app.before_request
    def load_access_token_middleware():
        access_token = get_access_token()
        if access_token:
            g.access_token = access_token
        else:
            g.access_token = None

    return app
