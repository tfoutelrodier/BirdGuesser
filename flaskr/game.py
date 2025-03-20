# -*- coding: utf-8 -*-
"""
Main game mode where you hear a sound and need to enter the bird name

"""
from io import BytesIO, StringIO

# import functools
import pandas as pd
import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, Response
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
        # Had issues with loading from json only. Added a way to load them as dict
        if isinstance(session['user_data_df'], dict):
            df = pd.DataFrame.from_dict(session['user_data_df'])
        else:
            # If it's a string, use StringIO
            df = pd.read_json(StringIO(session['user_data_df']), orient='split')
    elif 'data_df' in session:
        if isinstance(session['data_df'], dict):
            df = pd.DataFrame.from_dict(session['data_df'])
        else:
            # If it's a string, use StringIO
            df = pd.read_json(StringIO(session['data_df']), orient='split')
    else:
        return "No loaded data found", 404

    bird_data = df.sample(n=1)
    # id and english name are always present from database construction rules
    session['bird_name'] = str(bird_data['id'].iloc[0])  # temp id while waiting for data exraction to finish
    session['bird_id'] = str(bird_data['id'].iloc[0])
    # construct the link manually if missing for some reason
    print(bird_data['file'].iloc[0])
    print(session['bird_name'], session['bird_id'])
    if bird_data['file'].iloc[0] is not None:
        session['bird_sound_file'] = bird_data['file'].iloc[0]
    else:
        session['bird_sound_file'] = f"https://www.xeno-canto.org/{str(bird_data['id'].iloc[0])}/download"
    print(session['bird_sound_file'])
    return "", 200

@game_bp.route('/get_bird_sound_url', methods=['GET'])
def get_bird_sound_url():
    if 'bird_sound_file' in session:
        return jsonify({"url": session['bird_sound_file']}), 200
    else:
        return jsonify({"error": "No bird sound URL found"}), 404

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

# @game_bp.route('/get_session_attributes', methods=['GET'])
# def get_session_attributes():
#     if session:
#         return list(session.keys()), 200
#     else:
#         return "", 400