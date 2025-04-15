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


def test_game_index_success(client: FlaskClient):
    """
    Test loading index page.
    """
    response = client.get('/game/')
    assert response.status_code == 200


def test_select_random_bird_success(client, mocker, test_db_dict):
    """
    Test selecting a random bird.
    """
    test_bird: Bird = test_db_dict['bird_objects'][0]
    mock_db = setup_mock_db(mocker, __file__,  get_random_bird_from_set_return=test_bird)

    response = client.get(f"/game/get_random_bird_data/test_set")
    response_dict = response.get_json()
    assert response.status_code == 200
    assert isinstance(response_dict, dict)
    assert response_dict['name'] == test_bird.en
    assert response_dict['sound_url'] == test_bird.file


def test_select_random_bird_no_bird_found(client, mocker):
    """
    Test when the set has no birds inside.
    """
    mock_db = setup_mock_db(mocker, __file__,  get_random_bird_from_set_return=None)
    response = client.get(f"/game/get_random_bird_data/test_set")
    assert response.status_code == 404


def test_select_random_bird_no_set(client, mocker):
    """
    Test when the set doesn't exists.
    """
    mock_db = setup_mock_db(mocker, __file__,  get_random_bird_from_set_return=None)
    response = client.get(f"/game/get_random_bird_data")
    assert response.status_code == 404