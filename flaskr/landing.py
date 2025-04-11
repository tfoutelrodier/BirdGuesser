# -*- coding: utf-8 -*-
"""
Landing page when launching the game
Blueprint for this page
Allows to select between all options available (train and play at first)
"""
from flask import Blueprint, render_template, session

from flaskr.db import get_db

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """landing/home page with default informations"""
    db = get_db()

    if 'bird_name_list' not in session:
        session['bird_name_list'] = db.list_all_birds()

    return render_template('landing/index.html', 
                          title='BirdGuesser',
                          subtitle='Train to identify birds by their songs')