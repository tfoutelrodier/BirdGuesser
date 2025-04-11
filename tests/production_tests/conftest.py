# config file for pytest
# Set data for all test.
# Potential optimization : restrict perimeter of this file to test that actually need and app or client
import os
import sys

import pytest
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr import create_app

@pytest.fixture
def app() -> 'flask.Flask':
    """Create and configure a Flask app for testing."""
    app = create_app('production')

    # use yield for furture teardown code below this line
    yield app


@pytest.fixture
def client(app:'flask.Flask'):
    """Create a test client for the app in testing context."""
    return app.test_client()
