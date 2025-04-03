# -*- coding: utf-8 -*-
"""
Deal with the training mode
Training mode is where you are tested on a set of bird you have defined

Idea : create a table with all the records for the current session. Then select from it
"""

from flask import Blueprint, render_template, request, session, jsonify

from flaskr.db import add_bird_to_user_set, get_all_birds, get_birds_from_set
# from werkzeug.security import check_password_hash, generate_password_hash

# from db import get_db, create_profile_table
# from bird_set import init_user_profile

# bp = Blueprint('training', __name__, url_prefix='/training')
training_bp = Blueprint('training', __name__)


@training_bp.route('/', methods=('GET', 'POST'))
def index():
    """Page where user can creates bird sets to train on"""

     # default varaible that are used to update html when user answer a question
    song_url = ""  # No url present at first

    if request.method == 'POST':
        # Avoid capitalization issue
        bird_name = request.form.get('wantedBird', '').strip().lower()  
        bird_data = get_bird_data(session['data_path'], [bird_name])
        
        # construct the link manually if missing for some reason
        if bird_data.size == 0:
            return "Bird is not in database", 404
        
        session['bird_name'] = bird_name

        if bird_data['file'].iloc[0] is not None:
            session['bird_sound_file'] = bird_data['file'].iloc[0]
        else:
            session['bird_sound_file'] = f"https://www.xeno-canto.org/{str(bird_data['id'].iloc[0])}/download"
        song_url = session['bird_sound_file']  # THis could be done better, refactor later

    return render_template('training/index.html', 
                          title='BirdGuesser',
                          subtitle='Train to identify birds by their songs',
                          song_url=song_url)


@training_bp.route('/get_bird_name_list', methods=['GET'])
def get_bird_name_list():
    # return a json serialised list of all possible bird names
    if 'bird_name_list' in session:
        return jsonify(session['bird_name_list']), 200
    else:
        session['bird_name_list']
        return "Bird names not loaded in session", 404


@training_bp.route('add_to_user_set/<user_set>/<bird_name>', methods=['POST'])
def add_to_user_set(user_set: str, bird_name: str):

    if user_set != 'birds':
        add_bird_to_user_set(bird_name=bird_name, set_name=user_set)
        return "", 200
    else:
        return "Can't name a set 'birds'", 403


@training_bp.route('/get_birds_in_set/<set_name>')
def get_birds_in_set(set_name: str = None):
    """
    Return a list of all birds in a set
    if no set name, return all birds
    """
    if set_name is None:
        bird_lst = get_all_birds(set_name) 
    else:
        bird_lst = get_birds_from_set(set_name)
    
    if bird_lst == []:
        return "bird set not found", 404
    else:
        return bird_lst, 200
