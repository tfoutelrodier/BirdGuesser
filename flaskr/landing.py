# -*- coding: utf-8 -*-
"""
Landing page when launching the game
Blueprint for this page
Allows to select between all options available (train and play at first)
"""
import pathlib

from flask import Blueprint, render_template, session, current_app

from flaskr.db import load_random_rows_from_csv, load_bird_names, get_all_birds
from flaskr.helper import store_dataframe_in_session

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """landing/home page with default informations"""

    # load all birds for autocomplete purpose
    if 'bird_name_list' not in session:
        session['bird_name_list'] = get_all_birds()

    return render_template('landing/index.html', 
                          title='BirdGuesser',
                          subtitle='Train to identify birds by their songs')