import os
import sys
import numpy as np

import pandas as pd
from flask.testing import FlaskClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_select_random_bird(client: FlaskClient, test_df: pd.DataFrame) -> None:
    """
    Test selecting a random bird game route
     - Test if no stored data
     - Test if no user data stored
     - Test if User data stored
    """
    from flaskr.helper import df2json
    
    # Those are based on random selection so might have to be updated if uderlying function is modified
    expected_bird_name = 'Chestnut-capped Warbler'
    expected_bird_id = '540091'

    # check when no data
    response_no_data = client.get('/game/select_random_bird')
    assert response_no_data.status_code == 404

    # check when default data
    with client.session_transaction() as session:
        session['data_df'] = df2json(test_df)

    np.random.seed(0)
    response_default_data = client.get('/game/select_random_bird')
    assert response_default_data.status_code == 200

    with client.session_transaction() as session:
        print(session['bird_id'], session['bird_name'])
        assert session['bird_id'] == expected_bird_id
        assert session['bird_name'] ==  expected_bird_name

    # check when user data set
    with client.session_transaction() as session:
        session['user_data_df'] = df2json(test_df)

    np.random.seed(0)
    response_default_data = client.get('/game/select_random_bird')
    assert response_default_data.status_code == 200

    with client.session_transaction() as session:
        print(session['bird_id'], session['bird_name'])
        assert session['bird_id'] == expected_bird_id
        assert session['bird_name'] ==  expected_bird_name


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
