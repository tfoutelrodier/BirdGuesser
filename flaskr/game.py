# -*- coding: utf-8 -*-
"""
Main game mode where you hear a sound and need to enter the bird name

"""

# import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
# from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.bird_set import init_user_profile


bp = Blueprint('game', __name__)

@bp.route('/select_random_bird', methods=['GET'])
def select_random_bird() -> str:
    """
    Select a random element from current database
    """
    db = get_db()

    sql_command = """SELECT uid, id, en, file, file_name FROM table
                ORDER BY RAND()
                LIMIT 1"""
    
    bird_data = db.execute(sql_command)
    print(bird_data)
