# -*- coding: utf-8 -*-
"""
Landing page when launching the game
Blueprint for this page
Allows to select between all options available (train and play at first)
"""
import pathlib

from flask import Blueprint, render_template, session, current_app

from flaskr.db import get_db, load_random_rows_from_csv, load_bird_names
from flaskr.helper import df2json

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """landing/home page with default informations"""

    # # initialise some state (better to move them to )

    # data_path = pathlib.Path(current_app.root_path).joinpath('data').joinpath('french_bird_data.csv')
    # if 'data_path' not in session: 
    #     session['data_path'] = data_path.resolve()  # save data path is session as a quick way to reload data when needed to extract a bird name (might be better to use a sql db here for that)
        
    # # load random birds that will be used when playing on app launch
    # if 'data_df' not in session:
    #     # If the sample isn't in session, generate it
    #     data_df = load_random_rows_from_csv(data_path, 20)
    #     session['data_df'] = df2json(data_df)

    db = get_db()

    if 'bird_name_list' not in session:
        session['bird_name_list'] = db.list_all_birds()

    return render_template('landing/index.html', 
                          title='BirdGuesser',
                          subtitle='Train to identify birds by their songs')