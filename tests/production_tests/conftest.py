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


@pytest.fixture
def test_df() -> pd.DataFrame:
    # test dataset with two rows
    test_df = pd.DataFrame(
        [
            {
                'id':'542031',
                'gen':'Saltator',
                'sp':'olivascens',
                'en':'Olivaceous Saltator',
                'lat':'4.447',
                'lng':'-75.1535',
                'url':'//xeno-canto.org/542031',
                'file':'https://xeno-canto.org/542031/download',
                'file-name':'XC542031-Saltator coerulescens.mp3'
            },
            {
                'id':'540091',
                'gen':'Basileuterus',
                'sp':'delattrii',
                'en':'Chestnut-capped Warbler',
                'lat':'4.351',
                'lng':'-74.652',
                'url':'//xeno-canto.org/540091',
                'file':'https://xeno-canto.org/540091/download',
                'file-name':'XC540091-Rufous-capped Warbler.mp3'
            }
        ]
                            )
    return test_df