# config file for pytest
# Set data for all test.
# Potential optimization : restrict perimeter of this file to test that actually need and app or client
import os
import sys
from unittest.mock import MagicMock, ANY

from flask import Flask
from flask.testing import FlaskClient
# also need pytest-mock but not called here
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr import create_app
from flaskr.db_models import Bird

"""
Note: mocker fixture is a fixture created by default by pytest-mock, even without any definition
It's a wrapper around unit-test mock 
"""

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')

    # use yield for furture teardown code below this line
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app in testing context."""
    return app.test_client()


@pytest.fixture(scope='session')
def engine(app: Flask):
    db_file = app.config['DB_FILE']
    _engine = create_engine(f"sqlite+pysqlite:///{db_file}")

    # Use yied for automatic engine disposal at the end
    yield _engine
    _engine.dispose()


@pytest.fixture(autouse=True)
def mock_db(mocker):
    """Mocker for the Database class"""
    page_name_lst = [
        'training',
        'game',
        'landing'
    ]
    for page_name in page_name_lst:
        mocker.patch(f'flaskr.{page_name}.get_db')




@pytest.fixture(scope='function')
def test_bird_names() -> list[str]:
    """list of bird names present in test db"""
    bird_lst = [
        'Olivaceous Saltator',
        'Chestnut-capped Warbler',
        'Delicate Prinia',
        'Western Fire-eye',
        'Sulawesi Leaf Warbler',
        'West Mexican Euphonia',
        'Rennell Gerygone',
        'Red Fox',
        'Eurasian Particolored Bat'
    ]
    return bird_lst


@pytest.fixture(scope='function')
def test_db_dict() -> dict:
    """Dictionary with all data for mocking the database"""
    bird_dict = {
        'id':"978117",
        'gen':"Erithacus",
        'sp':"rubecula",
        'en':"European Robin",
        'lat':"41.8074",
        'lng':"-8.8626",
        'url':"//xeno-canto.org/978117",
        'file':"https://xeno-canto.org/978117/download",
        'file_name':"XC978117-Erithacus-rubecula_250302_184149_00.wav",
    }
    
    test_db_dict = {
        'set_name': 'test',
        'bird_objects': [Bird(**bird_dict)],
        'bird_name_list': ['European Robin']
        }
    return test_db_dict


# Function for setting a mock db for integration tests
def setup_mock_db(mocker,
                  file_name: str,
                  list_all_birds_return=None,
                  list_birds_in_set_return=None,
                  list_all_sets_return=None,
                  delete_user_set_return=None,
                  create_user_set_return=None,
                  add_bird_in_set_return=None,
                  remove_bird_from_set_return=None,
                  get_bird_return=None,
                  get_random_bird_from_set_return=None):
    """
    Creates a mock DB object for a Database object and its methods. Also patches get_db.
    Need to pass __file__ arguments to be able to attach the mock db correctly
    """
    mock_db = MagicMock()
    mock_db.list_all_birds.return_value = list_all_birds_return
    mock_db.list_birds_in_set.return_value = list_birds_in_set_return
    mock_db.list_all_sets.return_value = list_all_sets_return
    mock_db.delete_user_set.return_value = delete_user_set_return
    mock_db.create_user_set.return_value = create_user_set_return
    mock_db.add_bird_in_set.return_value = add_bird_in_set_return
    mock_db.remove_bird_from_set.return_value = remove_bird_from_set_return
    mock_db.get_bird.return_value = get_bird_return
    mock_db.get_random_bird_from_set.return_value = get_random_bird_from_set_return

    # attach to the correct page. File name should eb of type test_XXX.py
    page_name = os.path.basename(file_name).split('_', maxsplit=1)[1].rsplit(".", maxsplit=1)[0]
    mock_get_db = mocker.patch(f'flaskr.{page_name}.get_db')
    mock_get_db.return_value = mock_db
    return mock_db # Return the mock_db instance for potential assertion checks