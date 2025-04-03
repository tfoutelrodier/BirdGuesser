# -*- coding: utf-8 -*-
"""
Set up the flask server to have a queryable database with an API for bird guesser

# Start the server using flask --app flaskr run --debug
"""

import logging
import os

from cachelib.file import FileSystemCache  # to help configure session storage
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session

from flaskr.config.logging_config import setup_logging
from flaskr.data.create_db import create_database
from flaskr.db import close_db
from flaskr.helper import is_production
from flaskr.config.flask_config import config_dict, DevConfig

# blueprints
from flaskr.landing import landing_bp
from flaskr.game import game_bp
from flaskr.training import training_bp


# app factory
def create_app(config_name:str|None=None) -> Flask:
    """
    App factory to create Flask objects.
    config name is one of the allowed names in flask_config.py
    Allowed names are 'production, testing, development
    """

    app = Flask(__name__)

    load_dotenv()  # for loading sensitive data


    ### App config
    if config_name is None:
        config_name = os.environ.get('APP_TYPE', 'production')
    
    config_class = config_dict.get(config_name, DevConfig)
    app.config.from_object(config_class)
    
    if app.config.get('CONFIG_NAME', "") == 'testing':
        app.testing=True


    ### Logging
    logs_dir = app.config['LOGS_DIR']
    log_level = app.config['LOGS_LEVEL']
    # Create logs directory if it doesn't exist but not in prod for vercel
    if not is_production(app.config):
        os.makedirs(logs_dir, exist_ok=True)
    else:
        # This if satement doesn't do much but is kept due to older versions having bugs when deploying to vercel. 
        # Changes should have fixed the issue 
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
    
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


    ### Database
    # setup if doesn't exist
    database_file = app.config['DB_FILE']
    if not os.path.isfile(database_file):
        create_database(
            db_file=database_file,
            data_file=app.config['BIRD_DATA_FILE'],
            data_file_separator=app.config['BIRD_DATA_FILESEP']
        )

    ### Teardown procedure
    # Close db connection
    app.teardown_appcontext(close_db)


    ## Api requests 
    request_logs = {}


    ### Blueprints setup
    # Register blueprints
    app.register_blueprint(landing_bp, url_prefix='/')  # Set landing_bp as the root route
    app.register_blueprint(game_bp, url_prefix='/game')
    app.register_blueprint(training_bp, url_prefix='/training')

    logging.info("Flask app initialised")
    return app
