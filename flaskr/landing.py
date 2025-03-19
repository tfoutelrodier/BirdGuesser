# -*- coding: utf-8 -*-
"""
Landing page when launching the game
Blueprint for this page
Allows to select between all options available (train and play at first)
"""
import pathlib

from flask import Blueprint, render_template, session

from db import load_random_rows_from_csv, load_bird_names

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """landing page with default informations"""
    data_path = pathlib.Path('data/french_bird_data_test.csv')

    # load random birds that will be used when playing on app launch
    if 'data_df' not in session:
        # If the sample isn't in session, generate it
        data_df = load_random_rows_from_csv(data_path, 100)
        session['data_df'] = data_df.to_json(orient='split')  # Save as JSON

    if 'bird_name_list' not in session:
        session['bird_name_list'] = load_bird_names(data_path)
        

    return render_template('landing/index.html', 
                          title='BirdGuesser',
                          subtitle='Train to identify birds by their songs')