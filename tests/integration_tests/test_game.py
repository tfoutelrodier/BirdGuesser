import os
import sys
import numpy as np

import pandas as pd
from flask.testing import FlaskClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)


def test_game_index_get(client):
    """
    Test GET request to game index route
    - Test if correct template is rendered
    - Test that no message and no answer sent by default
    """
    response = client.get('/game/')
    
    assert response.status_code == 200
    data_txt = response.data.decode('utf-8')
    assert 'message' not in data_txt  # No default message
    assert 'correct_answer' not in data_txt  # No default correct answer


def test_game_index_post_correct_answer(client):
    """
    Test POST request to game index route
    - Test if correct message is returned when right
    - Test that message indicates correct answer
    """
    # First, set up the session with a bird name
    with client.session_transaction() as session:
        session['bird_name'] = 'Eagle'
    
    # Submit a matching answer
    response = client.post('/game/', data={'answer': 'Eagle'})
    
    assert response.status_code == 200
    data_txt = response.data.decode('utf-8')
    assert "Correct! It&#39;s indeed a eagle" in data_txt


def test_game_index_post_wrong_answer(client):
    """
    Test POST request to game index route
    - Test if correct message is returned when wrong
    - Test that message indicates correct answer
    """
    # First, set up the session with a bird name
    with client.session_transaction() as session:
        session['bird_name'] = 'Eagle'
    
    # Submit a matching answer
    response = client.post('/game/', data={'answer': 'Not_Eagle'})
    
    assert response.status_code == 200
    data_txt = response.data.decode('utf-8')
    assert "That&#39;s wrong! It was a eagle" in data_txt
