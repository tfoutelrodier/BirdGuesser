# -*- coding: utf-8 -*-
"""
Set up the flask server to have a queryable database with an API for bird guesser

# Start the server using flask --app flaskr run --debug
"""

import os
from pathlib import Path

from flask import Flask, render_template, current_app
from flask_session import Session
from dotenv import load_dotenv

# Import blueprints
from flaskr.landing import landing_bp
from flaskr.game import game_bp
from flaskr.training import training_bp


app = Flask(__name__)

load_dotenv()  # for loading snesitive data

# Data is stored in file server side because file could take a few Mb with sounds
app.config['SESSION_TYPE'] = 'filesystem'
session_folder = os.path.join(os.getcwd(), 'tmp', 'flask_sessions')
if not os.path.isdir(session_folder):
    os.makedirs(session_folder)  # Convert Path to string
app.config['SESSION_FILE_DIR'] = session_folder  # Use os.path for compatibility

app.config['SESSION_PERMANENT'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# limit API call to Xenocanto database to at most 1 request per time_window (in seconds)
app.config['API_TIME_WINDOW'] = 1  

# Initialize Flask-Session
Session(app)

request_logs = {}

# Register blueprints
app.register_blueprint(landing_bp, url_prefix='/')  # Set landing_bp as the root route
app.register_blueprint(game_bp, url_prefix='/game')
app.register_blueprint(training_bp, url_prefix='/training')