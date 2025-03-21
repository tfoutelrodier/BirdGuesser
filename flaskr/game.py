# -*- coding: utf-8 -*-
"""
Main game mode where you hear a sound and need to enter the bird name

"""
from io import StringIO
import time

# import functools
import pandas as pd
from flask import Blueprint, render_template, request, session, jsonify, current_app

from flaskr import globals  # for api tracking

game_bp = Blueprint('game', __name__)

@game_bp.route('/',  methods=['GET', 'POST'])
def index():
    """landing page for game"""
    
    # default varaible that are used to update html when user answer a question
    message = ""  # Default message
    correct_answer = ""  # Default answer

    if request.method == 'POST':
        # Avoid capitalization issue
        user_answer = request.form.get('answer', '').strip().lower()  
        correct_answer = session.get('bird_name', '').strip().lower()

        if user_answer == correct_answer:
            message = f"Correct! It's indeed a {correct_answer}"
        else:
            message = f"That's wrong! It was a {correct_answer}"


    return render_template('game/index.html', 
                          title='BirdGuesser',
                          subtitle='Time to play ! Can you identidy the birds ?',
                          message=message,
                          correct_answer=correct_answer)


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
    session['bird_name'] = str(bird_data['en'].iloc[0])  # temp id while waiting for data exraction to finish
    session['bird_id'] = str(bird_data['id'].iloc[0])

    # construct the link manually if missing for some reason
    if bird_data['file'].iloc[0] is not None:
        session['bird_sound_file'] = bird_data['file'].iloc[0]
    else:
        session['bird_sound_file'] = f"https://www.xeno-canto.org/{str(bird_data['id'].iloc[0])}/download"
    return "", 200


@game_bp.route('/get_bird_sound_url', methods=['GET'])
def get_bird_sound_url():
    # return the url to download a bird song from XenoCanto API
    
    # check for api usage rate
    user_ip = request.remote_addr
    current_time = time.time()
    last_request_time = globals.user_requests.get(user_ip, None)
    api_rate_limit = current_app.config.get('API_TIME_WINDOW', 2)  # Issue with recovering the api_rate_limit at the moment, use this to et default
    if last_request_time is not None:
        if current_time - last_request_time < api_rate_limit:
            # 429 is for rate limiting issues from what I saw
            return jsonify({"error": "Wait slightly before using trying again please"}), 429
        else:
            # Here I have an issue with thread safety for the future in case of multiple concurent users.
            # Could use threading.lock() to prevent this ?
            # Ignore for now
            globals.user_requests[user_ip] = current_time
    else:
        globals.user_requests[user_ip] = current_time

    if 'bird_sound_file' in session:
        return jsonify({"url": session['bird_sound_file']}), 200
    else:
        return jsonify({"error": "No bird sound URL found"}), 404


@game_bp.route('/get_bird_name_list', methods=['GET'])
def get_bird_name_list():
    # return a json serialised list of all possible bird names
    if 'bird_name_list' in session:
        return jsonify(session['bird_name_list']), 200
    else:
        return "Bird names not loaded in session", 404
    