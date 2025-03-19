# -*- coding: utf-8 -*-
"""
Landing page when launching the game
Blueprint for this page
Allows to select between all options available (train and play at first)
"""
from flask import Blueprint, render_template

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """landing page with default informations"""
    return render_template('landing/index.html', 
                          title='BirdGuesser',
                          subtitle='Train to identify birds by their songs')