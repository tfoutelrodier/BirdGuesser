# -*- coding: utf-8 -*-
"""
Set up the flask server to have a queryable database with an API for bird guesser

# Start the server using flask --app flaskr run --debug
"""

import os

from flask import Flask
from flask_session import Session
from cachelib.file import FileSystemCache  # to help configure session storage
from dotenv import load_dotenv

from flaskr.config.logging_config import setup_logging

# Import blueprints
from flaskr.landing import landing_bp
from flaskr.game import game_bp
from flaskr.training import training_bp
from flaskr.config.flask_config import config_dict


# app factory
def create_app(config_name:str='development') -> Flask:
    """
    App factory to create Flask objects.
    config name is one of the allowed names in flask_config.py
    Allowed names are 'production, testing, development
    """

    app = Flask(__name__)

    load_dotenv()  # for loading sensitive data

    ### App config
    app.config.from_object(config_dict.get(config_name, "development"))
    
    if config_name == 'testing':
        app.testing=True

    ### Logging
    logs_dir = app.config['LOGS_DIR']
    log_level = app.config['LOGS_LEVEL']
    os.makedirs(logs_dir, exist_ok=True) # Create logs directory if it doesn't exist
    setup_logging(logs_dir=logs_dir, log_level=log_level)

    ### Session
    # create session dir if needed
    session_folder = app.config['SESSION_FILE_DIR']
    if not os.path.isdir(session_folder):
        os.makedirs(session_folder)


    # Set session dir properly using FileSystemCache from cachelib
    session_cache = FileSystemCache(
        cache_dir=app.config['SESSION_FILE_DIR'], 
        threshold=app.config['SESSION_FILE_THRESHOLD'],
        default_timeout=app.config['SESSION_TIMEOUT_SECONDS']
    )
    app.config['SESSION_CACHELIB'] = session_cache

    # Initialize Flask-Session
    Session(app)

    request_logs = {}

    ### Blueprints setup
    # Register blueprints
    app.register_blueprint(landing_bp, url_prefix='/')  # Set landing_bp as the root route
    app.register_blueprint(game_bp, url_prefix='/game')
    app.register_blueprint(training_bp, url_prefix='/training')

    return app
