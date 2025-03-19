# -*- coding: utf-8 -*-
"""
Deal with the training mode
Training mode is where you are tested on a set of bird you have defined

Idea : create a table with all the records for the current session. Then select from it
"""

# import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db, create_profile_table
from flaskr.bird_set import init_user_profile

# bp = Blueprint('training', __name__, url_prefix='/training')
bp = Blueprint('training', __name__)

# @bp.route('/')
# def start_page():
#     db = get_db()
#     return render_template('base.html')


def load_all_birds(db):
    """
    Return a list of all birds available in the database
    For test UID are used rather than the full name
    """
    # Returns a list of tuple (1 tuple here)
    data_records = db.execute(
        "SELECT file_name FROM birds").fetchall()
    
    bird_lst = [record[0] for record in data_records]
    return(bird_lst)


@bp.route('/training', methods=('GET', 'POST'))
def training_bp():
    """Start a training session
    """
    if request.method == 'POST':
        
        # select a bird record
        db = get_db()
        
        # Get all possible UID
        # Returns a list of tuple (1 tuple here)
        uid_records = db.execute(
            "SELECT uid FROM birds").fetchall()

        g.bird_uid_lst = [uid[0] for uid in uid_records]

        # flash(error)

    return render_template('training/training.html')


@bp.route('/', methods=('GET', 'POST'))
def training_setup():
    """
    Define the training set
    """
    db = get_db()
    # If there are birds selected retrieve the corresponding data
    if not hasattr(g, "all_bird_lst"):
        g.all_bird_lst = load_all_birds(db)
        print(g.all_bird_lst)
    
    # initialise the profile is not already done
    init_user_profile()
    
    # print(g.all_bird_lst)
    return render_template('training/setup.html')


@bp.route('/create_user_set', methods=('GET', 'POST'))
def create_training_set():
    if request.method == 'POST':
        db = get_db()
        # create_profile_table(db, table_name)
        
