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
    def middleware():
        g.user_id = session.get("user_id")
        # print("middleware g.user_id: ", g.user_id)


        if not g.user_id:
            # print("No user_id found in session")
            return  # Exit early if no user_id is found
        # print("user_id ", g.user_id)
        g.user = get_user_by_id(g.user_id)
        if not g.user:
            # print("No user found with user_id:", g.user_id)
            return  # Exit early if user not found
        # print("user ", g.user)
        if "guid" not in g.user:
            # print("No guid found for user:", g.user)
            return
        # print("guid ", g.user["guid"])
        g.access_token = get_access_token_by_guid(g.user["guid"])
        if not g.access_token:
            # print("No access token found for guid:", g.user["guid"])
            return  # Exit early if access token not found
        
        # print("g values set: ", g.access_token, g.user_id, g.user["guid"])


    def clear_session_on_exit():
        """Clear session data when the app is shutting down."""
        with app.app_context():
            session.clear()
            print("Session cleared on application shutdown")

    # Register the clear function to run when the app exits
    # TODO: this gets an error when you ctrl+c to stop the server, idk if it needs a fix
    atexit.register(clear_session_on_exit)

    return app
