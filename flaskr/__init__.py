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
from flaskr.config import config_dict

# app factory
def create_app(config_name:str='development', test:bool=False) -> Flask:
    app = Flask(__name__)

    load_dotenv()  # for loading sensitive data

    app.config.from_object(config_dict.get(config_name, "development"))
    
    if config_name == 'testing':
        app.testing=True

    # create session dir if needed
    session_folder = app.config['SESSION_FILE_DIR']
    if not os.path.isdir(session_folder):
        os.makedirs(session_folder)

    # Initialize Flask-Session
    Session(app)

    request_logs = {}

    # Register blueprints
    app.register_blueprint(landing_bp, url_prefix='/')  # Set landing_bp as the root route
    app.register_blueprint(game_bp, url_prefix='/game')
    app.register_blueprint(training_bp, url_prefix='/training')

    return app
