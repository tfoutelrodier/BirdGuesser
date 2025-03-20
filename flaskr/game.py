# -*- coding: utf-8 -*-
"""
Main game mode where you hear a sound and need to enter the bird name

"""
from io import BytesIO, StringIO

# import functools
import pandas as pd
import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
# from werkzeug.security import check_password_hash, generate_password_hash

# from db import get_db
# from bird_set import init_user_profile


game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def index():
    """landing page for game"""

    return render_template('game/index.html', 
                          title='BirdGuesser',
                          subtitle='Time to play ! Can you identidy the birds ?')


@game_bp.route('/select_random_bird', methods=['GET'])
def select_random_bird() -> str:
    """
    Select a random element from current loaded data 
    Store it in the session (update if needed)
    """
    # load user dataset or random dataset if absent
    if 'user_data_df' in session:
        df = pd.read_json(StringIO(session['user_data_df']), orient='split')
    elif 'data_df' in session:
        df = pd.read_json(StringIO(session['data_df']), orient='split')
    else:
        return "No loaded data found", 404

    bird_data = df.sample(n=1)
    # id and english name are always present from database construction rules
    session['bird_name'] = bird_data['id']  # temp id while waiting for data exraction to finnish
    session['bird_id'] = bird_data['id']
    # construct the link manually if missing for some reason
    if bird_data['file'] != '':
        session['bird_sound_file'] = bird_data['file']
    else:
        session['bird_sound_file'] = f"https://www.xeno-canto.org/{bird_data['id']}/download"
    return 200


@game_bp.route('/get_bird_sound_url', methods=['GET'])
def get_bird_sound_url():
    if 'bird_sound_url' in session:
        return session['bird_sound_url'], 200
    else:
        return None, 404

    """ # load a mp3 sound in session from xenocanto database
    if 'bird_sound_url' not in session:
        return "No loaded bird data", 404

    # Download the sound file
    response = requests.get(session['bird_sound_url'])

    if response.status_code != 200:
        return "Can't load bird data", response.status_code

    # Store the sound file as a BytesIO object
    session['sound_file'] = BytesIO(response.content)
    return 200 """

    # sql_command = """SELECT uid, id, en, file, file_name FROM table
    #             ORDER BY RAND()
    #             LIMIT 1"""
    
    # bird_data = db.execute(sql_command)
    # print(bird_data)

@game_bp.route('/get_session_attributes', methods=['GET'])
def get_session_attributes():
    if session:
        return list(session.keys()), 200
    else:
        return "", 999