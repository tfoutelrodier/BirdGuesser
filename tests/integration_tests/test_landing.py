import os
import sys
from unittest.mock import MagicMock, ANY

from flask.testing import FlaskClient
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr.db_models import Bird
from conftest import setup_mock_db

"""
Note: mocker fixture is a fixture created by default by pytest-mock, even without any definition
It's a wrapper around unit-test mock 
"""

#######
# Tests
#######


def test_landing_index_success(client: FlaskClient, mocker, test_db_dict):
    """
    Test loading index page.
    """
    bird_lst = test_db_dict['bird_name_list']
    mock_db = setup_mock_db(mocker, __file__,  list_all_birds_return=bird_lst)

    response = client.get('/')
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert 'bird_name_list' in sess
        assert sess['bird_name_list'] == bird_lst
        

def test_landing_index_previous_session_data(client: FlaskClient, mocker, test_db_dict):
    """
    Test loading index page with some bird name data already in session.
    """
    bird_lst = test_db_dict['bird_name_list']
    alternative_bird_lst = ['wrong bird']
    mock_db = setup_mock_db(mocker, __file__, list_all_birds_return=bird_lst)

    # preload session with data
    with client.session_transaction() as sess:
        assert 'bird_name_list' not in sess
        sess['bird_name_list'] = alternative_bird_lst
        assert 'bird_name_list' in sess

    response = client.get('/')
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert 'bird_name_list' in sess
        assert sess['bird_name_list'] != bird_lst  # assert that data was not overwritten
        assert sess['bird_name_list'] == alternative_bird_lst