# -*- coding: utf-8 -*-
"""
Functions required to load, update and save a bird set
"""

import sqlite3
from flask import (
    Blueprint, g, redirect, render_template, request, session, url_for, jsonify
)
from flaskr.db import get_db, records2list_of_dict


bp = Blueprint('bird_set', __name__, url_prefix='/bird_set')



def init_user_profile():
    '''
    Load previous profile if exist
    At the moment just initialize two empty list
    One for focus birds and one for rare_birds
    '''
    if not hasattr(g, 'focus_bird_lst'):
        g.focus_bird_lst = ['toto']
    
    if not hasattr(g, 'focus_bird_lst'):
        g.rare_bird_lst = ['polp']


def create_user_profile(profile_name):
    """
    Create a table with the user profile name
    """
    db = get_db()
    
    # Returns a list of tuple (1 tuple here)
    data_records = db.execute(
        "SELECT file_name FROM birds").fetchall()
    
    
@bp.route('/get_birds_in_set', methods=('GET'))
def get_birds_in_set():
    '''
    takes a 'get' request with parameter set_name
    Return the list of bird name (uid for test) in this user set
    If set doesn't exist return error'
    '''
    if request.method != 'GET':
        return(jsonify({"error": "Only supports GET request"}), 400)
    
    set_name = request.args.get('set_name')
    if not set_name:
        return(jsonify({"error": "Missing parameter: 'set_name'"}), 400)
    elif set_name == 'birds':
        return(jsonify({"error": "can't create a set with name: birds"}), 400)
    
    # get database querry:
    db = get_db()
    columns_to_select = ['uid']
    try:
        sql_query = f"SELECT {','.join(columns_to_select)} FROM {set_name}"
    except sqlite3.OperationalError:
        return(jsonify({"error": "table doesn't exist"}), 404)
    
    data_records = db.execute(sql_query).fetchall()
    
    if len(data_records) != 0:
        # Convert data to list of dict
        return_data = records2list_of_dict(data_records, columns_to_select)
        return(jsonify(return_data), 200)
    else:
        return(jsonify({}), 204)
    

@bp.route('/add_bird_to_set', methods=('POST'))
def add_bird_to_set():
    """
    Add bird data to set
    Input is bird name and bird_set_name
    Request bird data from main table
    Add to set table (create if needed)
    """
    if request.method != 'POST':
        return(jsonify({"error": "Only supports POST request"}), 400)
    
    db = get_db()
    # assume JSON data for now
    data = request.get_json()
    bird_name = data.get('bird_name')
    bird_set_name = data.get('bird_set_name')
    
    # extract bird data from birds table
    
    
    
    # check if user table exists
    
    # intsert into table
    
    
    