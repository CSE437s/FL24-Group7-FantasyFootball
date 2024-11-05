# app/__init__.py

from flask import Flask, g, session
import os
from dotenv import load_dotenv
from .db import create_access_tokens_table, get_user_by_id, get_access_token_by_guid
from .routes import api, main
from flask_session import Session  # Import Flask-Session extension

def create_app():
    load_dotenv(override=True)

    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    # Optional: Configure Flask-Session to store session data on the server side
    app.config["SESSION_TYPE"] = "filesystem"  # Store session data in the filesystem
    Session(app)  # Initialize the Flask-Session extension

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(main)

    create_access_tokens_table()

    @app.before_request
    def load_access_token_middleware():
        user_id = session.get("user_id")
        if user_id:
            g.user_id = user_id
            user = get_user_by_id(user_id)
            if user:
                access_token = get_access_token_by_guid(user["guid"])
                if access_token:
                    g.access_token = access_token
                else:
                    g.access_token = None
            else:
                g.access_token = None
        else:
            g.access_token = None

    return app
