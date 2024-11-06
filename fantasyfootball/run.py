# app/main.py

from flask import Flask, redirect, request, jsonify, render_template
from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
import os
from dotenv import load_dotenv
from app import create_app
from app.routes import api, main


# Load environment variables
load_dotenv()

app = create_app()
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(main)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print(app.url_map)  # Add this line to print the URL map
    app.run(debug=True, host='0.0.0.0', port=3000, ssl_context=('cert.pem', 'key.pem'))
