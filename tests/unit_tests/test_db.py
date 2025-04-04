import random
import os
import pathlib
import sys

import pandas as pd
import pytest
from sqlalchemy import create_engine


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr import db

# add data_path as a keyword args to test for this file
@pytest.fixture
def data_path() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(__file__)) / '..' / 'data' / 'test_bird_data.csv'


@pytest.fixture
def database_engine() -> 'sqlalchemy.engine.Engine':
    # create a database in memory to test db functions
    engine = create_engine(f"sqlite+pysqlite:///:memory:", echo=True)
    return engine


def test_load_random_rows_from_csv(data_path: pathlib.Path) -> None:
    random.seed(0)
    selected_row = db.load_random_rows_from_csv(data_path, nb_rows=1)
    selected_id = int(selected_row['id'].values[0])
    assert selected_id == 511425


def test_load_bird_name(data_path: pathlib.Path) -> None:
    expected_bird_name_list = [
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
    assert db.load_bird_names(data_path) == expected_bird_name_list


# def test_get_bird_data_single_bird(data_path: pathlib.Path) -> None:
#     bird_name = ['Olivaceous Saltator']
#     test_bird_data = pd.DataFrame(
#         [{
#             'id':'542031',
#             'gen':'Saltator',
#             'sp':'olivascens',
#             'en':'Olivaceous Saltator',
#             'lat':'4.447',
#             'lng':'-75.1535',
#             'url':'//xeno-canto.org/542031',
#             'file':'https://xeno-canto.org/542031/download',
#             'file-name':'XC542031-Saltator coerulescens.mp3'
#         }]
#                             )

#     bird_data = db.get_bird_data(data_path, bird_names=bird_name)
#     print(bird_data)
#     pd.testing.assert_frame_equal(bird_data, test_bird_data)


# def test_get_bird_data_multiple_birds(data_path: pathlib.Path) -> None:
#     bird_names = ['Olivaceous Saltator', 'Chestnut-capped Warbler']
#     test_bird_data = pd.DataFrame(
#         [
#             {
#                 'id':'542031',
#                 'gen':'Saltator',
#                 'sp':'olivascens',
#                 'en':'Olivaceous Saltator',
#                 'lat':'4.447',
#                 'lng':'-75.1535',
#                 'url':'//xeno-canto.org/542031',
#                 'file':'https://xeno-canto.org/542031/download',
#                 'file-name':'XC542031-Saltator coerulescens.mp3'
#             },
#             {
#                 'id':'540091',
#                 'gen':'Basileuterus',
#                 'sp':'delattrii',
#                 'en':'Chestnut-capped Warbler',
#                 'lat':'4.351',
#                 'lng':'-74.652',
#                 'url':'//xeno-canto.org/540091',
#                 'file':'https://xeno-canto.org/540091/download',
#                 'file-name':'XC540091-Rufous-capped Warbler.mp3'
#             }
#         ]
#                             )

#     birds_data = db.get_bird_data(data_path, bird_names=bird_names)
#     pd.testing.assert_frame_equal(birds_data, test_bird_data)


# def test_get_bird_data_wrong_bird(data_path: pathlib.Path) -> None:
#     bird_name = ['Nope Bird']
#     bird_data = db.get_bird_data(data_path, bird_name)
#     assert len(bird_data) == 0


def test_get_engine(app, client) -> None:
    with client:
        with app.app_context():
            from flaskr.db import get_engine
            from sqlalchemy.engine import Engine
            from flask import g
            engine = get_engine()
            assert type(engine) is Engine
            assert 'db_engine' in g


def test_connect_to_database(app, client) -> None:
    with client:
        with app.app_context():
            from flaskr.db import connect_to_database
            from sqlalchemy.orm import scoped_session
            session = connect_to_database()
            assert type(session) is scoped_session


def test_get_and_close_db(app, client) -> None:
    with client:
        with app.app_context():
            from flaskr.db import get_db, close_db
            from sqlalchemy.orm import scoped_session
            from flask import g
            
            db = get_db()
            assert type(db) is scoped_session
            assert 'db' in g 
            close_db()
            assert 'db' not in g

