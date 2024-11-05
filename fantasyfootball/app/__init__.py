# app/__init__.py

from flask import Flask, g, session
import os
from dotenv import load_dotenv
from .db import (
    create_access_tokens_table,
    get_user_by_id,
    get_access_token_by_guid,
    create_users_table,
)
from .routes import api, main
from flask_session import Session  # Import Flask-Session extension
import atexit


def create_app():
    load_dotenv(override=True)

    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(main)

    create_access_tokens_table()
    create_users_table()

    @app.before_request
    def load_access_token_middleware():
        user_id = session.get("user_id")
        user_guid = session.get("curr_user_guid")
        print("middleware user guid: ",user_guid)


        # Default values for g in case conditions aren't met
        g.access_token = None
        g.user_id = None
        g.user_guid = None

        if not user_id:
            return  # Exit early if no user_id is found
        print("user_id ",user_id)
        user = get_user_by_id(user_id)
        if not user:
            return  # Exit early if user not found
        print("user ",user)
        print("guid ",user["guid"])
        access_token = get_access_token_by_guid(user["guid"])
        if not access_token:
            return  # Exit early if access token not found

        # If all checks pass, set g variables
        g.access_token = access_token
        g.user_id = user_id
        g.user_guid = user["guid"]

    def clear_session_on_exit():
        """Clear session data when the app is shutting down."""
        with app.app_context(): 
            session.clear()
            print("Session cleared on application shutdown")

    # Register the clear function to run when the app exits
    #TODO: this gets an error when you ctrl+c to stop the server, idk if it needs a fix
    atexit.register(clear_session_on_exit)

    return app
