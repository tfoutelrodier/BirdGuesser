# -*- coding: utf-8 -*-
"""
Main game mode where you hear a sound and need to enter the bird name

"""
from io import StringIO
import logging
import time

# import functools
import pandas as pd
from flask import Blueprint, render_template, request, session, jsonify, current_app

from flaskr import globals  # for api tracking
from flaskr.db import get_db

game_bp = Blueprint('game', __name__)

@game_bp.route('/', methods=['GET'])
def index():
    """landing page for game"""
    
    # # default varaible that are used to update html when user answer a question
    # message = ""  # Default message
    # correct_answer = ""  # Default answer

    # if request.method == 'POST':
    #     # Avoid capitalization issue
    #     user_answer = request.form.get('answer', '').strip().lower()  
    #     correct_answer = session.get('bird_name', '').strip().lower()

    #     if user_answer == correct_answer:
    #         message = f"Correct! It's indeed a {correct_answer}"
    #     else:
    #         message = f"That's wrong! It was a {correct_answer}"


    return render_template('game/index.html')
                        #   title='BirdGuesser',
                        #   subtitle='Time to play ! Can you identidy the birds ?',
                        # #   message=message,
                        # #   correct_answer=correct_answer)


@game_bp.route('/get_random_bird_data', methods=['GET'])
@game_bp.route('/get_random_bird_data/<set_name>', methods=['GET'])
def select_random_bird(set_name:str|None=None) -> dict[str:str]:
    """
    Return a dictionary with data from a random bird from a given set.
    """
    db = get_db()

    if set_name is None:
        logging.error("No bird set selected")
        return "", 404
    logging.debug(f'db is of type: {type(db)}')
    random_bird =  db.get_random_bird_from_set(set_name)

    # check if data was actually selected
    if random_bird is None:
        logging.error(f"Couldn't load a bird from user_set {set_name}")
        return "", 404
    
    return_dict = {
        'name': random_bird.en,
        'sound_url': random_bird.file
    }

    return return_dict, 200




# @game_bp.route('/select_random_bird', methods=['GET'])
# def select_random_bird() -> str:
#     """
#     Select a random element from current loaded data 
#     Store it in the session (update if needed)
#     """
#     # load user dataset or random dataset if absent
#     if 'user_data_df' in session:
#         df = json2df(session['user_data_df'])
#         current_app.logger.info(f"loaded 'user_data_df' from session")
#         # df = load_df_from_session(key='user_data_df')
#     elif 'data_df' in session:
#         df = json2df(session['data_df'])
#         current_app.logger.info(f"loaded 'data_df' from session")
#         # df = load_df_from_session(key='data_df')
#     else:
#         current_app.logger.info(f"Couldn't load dataframe because missing session key")
#         return "No loaded data found", 404

#     bird_data = df.sample(n=1)
#     # id and english name are always present from database construction rules
#     session['bird_name'] = str(bird_data['en'].iloc[0])  # temp id while waiting for data exraction to finish
#     session['bird_id'] = str(bird_data['id'].iloc[0])

#     # construct the link manually if missing for some reason
#     if bird_data['file'].iloc[0] is not None:
#         session['bird_sound_file'] = bird_data['file'].iloc[0]
#     else:
#         session['bird_sound_file'] = f"https://www.xeno-canto.org/{str(bird_data['id'].iloc[0])}/download"
#     return "", 200


@game_bp.route('/get_bird_sound_url', methods=['GET'])
def get_bird_sound_url():
    # return the url to download a bird song from XenoCanto API
    
    # check for api usage rate
    user_ip = request.remote_addr
    current_time = time.time()
    last_request_time = globals.user_requests.get(user_ip, None)
    api_rate_limit = current_app.config.get('API_TIME_WINDOW', 1)  # Issue with recovering the api_rate_limit at the moment, use this to et default
    if last_request_time is not None:
        if current_time - last_request_time < api_rate_limit:
            # 429 is for rate limiting issues from what I saw
            return {"error": "Wait slightly before using trying again please"}, 429
        else:
            # Here I have an issue with thread safety for the future in case of multiple concurent users.
            # Could use threading.lock() to prevent this ?
            # Ignore for now
            globals.user_requests[user_ip] = current_time
    else:
        globals.user_requests[user_ip] = current_time

    if 'bird_sound_file' in session:
        return {"url": session['bird_sound_file']}, 200
    else:
        return {"error": "No bird sound URL found"}, 404


@game_bp.route('/get_bird_name_list', methods=['GET'])
def get_bird_name_list():
    # return a json serialised list of all possible bird names
    if 'bird_name_list' in session:
        return session['bird_name_list'], 200
    else:
        return "Bird names not loaded in session", 404
    