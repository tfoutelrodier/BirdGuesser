# Main file
# Run using python BirdGuesser/flaskr/app.py
import os

from flask import Flask, render_template, current_app
from flask_session import Session

# Import blueprints
from landing import landing_bp
from game import game_bp
from training import training_bp
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # for loading snesitive data

# Data is stored in file server side because file could take a few Mb with sounds
app.config['SESSION_TYPE'] = 'filesystem'
# use os.getcwd rather than current_app because outside of app at the moment
session_folder = os.path.join(os.getcwd(), 'tmp', 'flask_sessions')
if not os.path.isdir(session_folder):
    os.makedirs(session_folder) 
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'tmp', 'flask_sessions')

app.config['SESSION_PERMANENT'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# limit API call to Xenocanto database to at most 1 request per time_window (in seconds)
app.config['API_TIME_WINDOW'] = 1  

# Initialize Flask-Session
Session(app)

request_logs = {}

# Register blueprints
app.register_blueprint(landing_bp)
app.register_blueprint(game_bp, url_prefix='/game')
app.register_blueprint(training_bp, url_prefix='/training')

if __name__ == '__main__':
    # for local run
    # app.run(debug=True)
    # for vercel hosting
    app.run(host="0.0.0.0", port=8080, debug=True)