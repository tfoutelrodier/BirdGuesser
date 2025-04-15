# -*- coding: utf-8 -*-
"""
Training page
- You can listen to whatever bird song you want
- You can create, delete and load custom sets for playing the game
"""

import logging

from flask import Blueprint, render_template, request, session, jsonify, current_app

from flaskr.db import get_db
# from werkzeug.security import check_password_hash, generate_password_hash

# from db import get_db, create_profile_table
# from bird_set import init_user_profile

# bp = Blueprint('training', __name__, url_prefix='/training')
training_bp = Blueprint('training', __name__)


@training_bp.route('/', methods=['GET'])
def index():
    """Page where user can creates bird sets to train on"""
    return render_template('training/index.html')


@training_bp.route('/get_bird_name_list', methods=['GET'])
def get_bird_name_list():
    # return a list of all possible bird names
    if 'bird_name_list' in session:
        return session['bird_name_list'], 200
    else:
        # session['bird_name_list']
        return "Bird names not loaded in session", 404


@training_bp.route('/get_birds_in_set')
@training_bp.route('/get_birds_in_set/<set_name>')
def get_birds_in_set(set_name: str = None):
    """
    Return a list of all birds in a set
    if no set name, return all birds
    """
    db = get_db()
    if set_name is None or set_name == "":
        bird_lst = db.list_all_birds() 
    else:
        bird_lst = db.list_birds_in_set(set_name)
    logging.debug(f"bird set {set_name} has {bird_lst}")

    if bird_lst is None or bird_lst == []:
        return "bird set not found", 404
    else:
        return bird_lst, 200


@training_bp.route('/get_user_sets', methods=['GET'])
@training_bp.route('/get_user_sets/<option>', methods=['GET'])
def get_user_sets(option: str='all'):
    """
    Returns a list of all created user sets
    If none, returns an empty list
    With option = default, returns the list of default sets that shouldn't be modified or deleted

    args: 
        option: str, a value from ['all', 'default']
    """
    set_lst = []
    db = get_db()
    if option == 'all':
        set_lst = db.list_all_sets()
    elif option == 'default':
        set_lst = current_app.config['DEFAULT_SET_LIST']
    else:
        error_message = f'invalid option in get_user_sets: {option}'
        logging.error(error_message)
        return [], 400
    return set_lst, 200


@training_bp.route('/delete_set/<set_name>', methods=['POST'])
def delete_set(set_name: str|None):
    """
    Delete a user set from the database
    """
    if set_name is None:
        return "No set name provided", 404
    elif request.method != 'POST':
        return "Only post method is supported", 404
    
    db = get_db()
    is_deleted = db.delete_user_set(set_name)
    if is_deleted:
        return "", 200
    else:
        return "", 404 


@training_bp.route('/create_set/<set_name>', methods=['POST'])
def create_set(set_name: str|None):
    """
    create an empty user with name set_name set in the database
    """
    if set_name is None:
        return "No set name provided", 404
    elif request.method != 'POST':
        return "Only post method is supported", 404
    
    db = get_db()
    is_created = db.create_user_set(set_name)
    if is_created:
        return "", 200
    else:
        return "", 404 


@training_bp.route('add_to_user_set/<user_set>/<bird_name>', methods=['POST'])
def add_to_user_set(user_set: str, bird_name: str):
    """
    Add bird to set in dataabse
    """
    if request.method != 'POST':
        return "Only post method is supported", 404

    db = get_db()
    is_added = db.add_bird_in_set(bird_name, user_set)
    if is_added:
        return "", 200
    else:
        return "", 404
    

@training_bp.route('remove_bird_from_set/<user_set>/<bird_name>', methods=['POST'])
def remove_bird_from_set(user_set: str, bird_name: str):
    """
    remove bird from set in dataabse
    """
    if request.method != 'POST':
        return "Only post method is supported", 404

    db = get_db()
    is_deleted = db.remove_bird_from_set(bird_name, user_set)
    if is_deleted:
        return "", 200
    else:
        return "", 404
    

@training_bp.route('get_bird_song/<bird_name>', methods=['GET'])
def get_bird_song(bird_name: str=""):
    """
    get a bird_song url
    """
    if request.method != 'GET':
        return "Only get method is supported", 405

    db = get_db()
    bird_obj = db.get_bird(bird_name)
    if bird_obj is None:
        logging.info(f"Bird {bird_name} not found")
        return "", 404
    
    if bird_obj.file is None:
        logging.info(f"No song file for bird {bird_obj.id} -- {bird_obj.en}")
        return "", 404
    
    song_url = bird_obj.file
    return song_url, 200
    