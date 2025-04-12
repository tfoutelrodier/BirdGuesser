# config file for pytest
# Set data for all test.
# Potential optimization : restrict perimeter of this file to test that actually need and app or client
import os
import sys

from flask import Flask
from flask.testing import FlaskClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr import create_app
from flaskr.db import Database


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


@pytest.fixture(scope='function')
def db(engine: Engine):
    """Fixture to create a Database class instance connected to engine."""
    db = Database(engine)
    yield db
    db.close_db()


