import os
import sys
import numpy as np

import pandas as pd
from flask.testing import FlaskClient
from flaskr import create_app

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)


def test_is_production_prod(app):
    app = create_app('production')
    from flaskr.helper import is_production
    assert is_production(app.config) == True


def test_prod_config(app):
    app = create_app('production')
    assert app.config['CONFIG_TYPE'] == 'production'
    assert app.config['SESSION_FILE_DIR'] == '/tmp'
    assert app.config['LOGS_DIR'] == '/tmp/logs'
