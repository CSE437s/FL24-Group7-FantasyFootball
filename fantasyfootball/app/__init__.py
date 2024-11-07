from flask import Flask
from app.db import create_player_data_table

def create_app():
    app = Flask(__name__)
    create_player_data_table()
    return app