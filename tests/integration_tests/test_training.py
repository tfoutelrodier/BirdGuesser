import os
import sys

from flask import Flask
from flask.testing import FlaskClient

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)


def test_index_get(client: FlaskClient):
    """Test GET on default page"""
    response = client.get('/training/')
    assert response.status_code == 200
 