import random
import os
import pathlib
import sys

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.engine import Engine

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr.db import Database
from flaskr.db_models import Base, Bird, UserSet

# TEST_DB_FILE = os.path.join(root_dir, 'tests', 'data', 'test_db.db')
TEST_DB_FILE = "sqlite://"  # defaults to memory

# add data_path as a keyword args to test for this file
@pytest.fixture
def data_path() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(__file__)) / '..' / 'data' / 'test_bird_data.csv'
    

@pytest.fixture
def db_file() -> str:
    return os.path.join(root_dir, 'flaskr', 'data', 'birds_db.db')


@pytest.fixture(scope='session')
def engine():
    if TEST_DB_FILE.startswith("sqlite"):
        _engine = create_engine(TEST_DB_FILE)
        # if in memry create empty tables
        Base.metadata.create_all(_engine)  
    else:
        _engine = create_engine(f"sqlite+pysqlite:///{TEST_DB_FILE}")

    # Use yied for automatic engine disposal at the end
    yield _engine
    _engine.dispose()


@pytest.fixture(scope='function')
def db(engine: Engine) -> Database:
    """Fixture to create a Database class instance connected to engine."""
    db = Database(engine)
    yield db
    db.close_db()


@pytest.fixture(scope='function')
def empty_tables(db: Database) -> Database:
    """Create empty tables in the database"""
    Base.metadata.create_all(db.engine)
    return db


@pytest.fixture(scope="function")
def test_db(db: Database, empty_tables:Database, data_path: pathlib.Path) -> Database:
    """
    Fixture to add default test data to the database.
    Use sqlalchemy functions to populate database in order to test custom methods later.
    """
    db = empty_tables

    # load the test bird data
    test_bird_df = pd.read_csv(data_path, header=0, sep="|")
    bird_dict_lst = test_bird_df.to_dict('records')
    # print(bird_dict_lst)
    bird_lst = [Bird(**bird_dict) for bird_dict in bird_dict_lst]
    print(bird_lst)
    db.db.add_all(bird_lst)
    db.db.commit()
    
    # create test user set
    test_set = UserSet(set_name='test')
    test_set2 = UserSet(set_name='test_multiple_birds')
    empty_set = UserSet(set_name='empty_set')
    db.db.add_all([test_set, test_set2, empty_set])
    db.db.commit()

    # Add birds to set
    test_bird = db.db.query(Bird).filter(Bird.en == "Olivaceous Saltator").one()
    test_bird2 = db.db.query(Bird).filter(Bird.en == "Delicate Prinia").one()
    
    test_set = db.db.query(UserSet).filter(UserSet.set_name == "test").one()
    test_set2 = db.db.query(UserSet).filter(UserSet.set_name == "test_multiple_birds").one()
    
    test_set.birds.append(test_bird)
    test_set2.birds.append(test_bird)
    test_set2.birds.append(test_bird2)
    db.db.commit()

    return db


@pytest.fixture(scope='function')
def test_bird_names() -> list[str]:
    """Names of the birds in the test db fixture"""
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
def new_bird() -> Bird:
    """New bird object to test adding to db"""
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
    new_bird = Bird(**bird_dict)
    return new_bird


@pytest.fixture(scope='function')
def new_set() -> UserSet:
    """New userSet object to add to db"""
    new_set = UserSet(set_name='new_set')
    return new_set


####
# Test access to database in app
####

def test_connect_to_database(app, client) -> None:
    with client:
        with app.app_context():
            from flaskr.db import connect_to_database
            from sqlalchemy.orm import scoped_session
            session = connect_to_database()
            assert type(session) is scoped_session


def test_get_engine(app, client):
    """Test storing and retrieving from the g object"""
    with client:
        with app.app_context():
            from flaskr.db import get_engine
            from flask import g
            engine = get_engine()
            assert isinstance(engine, Engine)
            assert 'db_engine' in g


def test_get_and_close_db(app, client) -> None:
    with client:
        with app.app_context():
            from flaskr.db import get_db, close_db, Database
            from flask import g
            
            db = get_db()
            assert type(db) is Database
            assert 'db' in g 
            close_db()
            assert 'db' not in g


def test_connect_to_database(app) -> None:
    with app.app_context():
        from flaskr.db import connect_to_database, Database
        from sqlalchemy.engine import Engine
        from sqlalchemy.orm import scoped_session
        
        db = connect_to_database()
        assert type(db) is Database
        assert type(db.engine) is Engine
        assert type(db.db) is scoped_session


######
# Test Database Class
######

    ####
    # Test empty database
    ####

def test_db_instance_creation(db: Database):
    """
    Test if the fixtures are create correctly
    """
    assert db is not None
    assert db.engine is not None
    assert db.db is not None
    assert isinstance(db.engine, Engine)
    assert isinstance(db.db, scoped_session)
    assert isinstance(db, Database)
    assert db.db.bind == db.engine  # Check that the engine is connected to the database session


def test_list_all_sets_empty_db(db: Database):
    """ Test that the set list is empty"""
    assert db.list_all_sets() == []


def test_list_all_birds_empty_db(db: Database):
    """ Test that the bird list is empty"""
    assert db.list_all_birds() == []


#
    ######
    # Test database with empty tables
    ######

def test_list_all_sets_empty_tables(empty_tables: Database):
    db = empty_tables
    assert isinstance(db, Database)
    user_sets = db.list_all_sets()
    assert user_sets == []


def test_list_all_birds_test_db(empty_tables: Database):
    """Test if returns birds on populated database """
    db = empty_tables
    bird_lst = db.list_all_birds()
    assert bird_lst == []


def test_create_user_set(empty_tables: Database):
    """Test adding to table"""
    db = empty_tables
    set_name = 'new_set'
    test_set = db.create_user_set(set_name=set_name)
    assert isinstance(test_set, UserSet)
    assert test_set.set_name == set_name

    # check if in dataabse
    recovered_set = db.db.query(UserSet).filter(UserSet.set_name == set_name).first()
    assert isinstance(recovered_set, UserSet)
    assert recovered_set.id == test_set.id  # check that id match


#
    ######
    # Test database with test data
    ######

def test_list_all_sets_test_db(test_db: Database):
    """ Test that the set list holds the test set"""
    db = test_db
    assert isinstance(db, Database)  # check fixture
    user_sets = db.list_all_sets()
    assert isinstance(user_sets, list)
    assert user_sets == ['test', 'test_multiple_birds', 'empty_set']


def test_list_all_birds_test_db(test_db: Database, test_bird_names: list):
    """Test if returns birds on populated database """
    db = test_db
    bird_lst = db.list_all_birds()
    print('TOTO')
    assert isinstance(bird_lst, list)
    assert isinstance(test_bird_names, list)
    assert len(bird_lst) == len(test_bird_names)
    assert set(bird_lst) == set(test_bird_names)  # test that all bird names are present


def test_add_bird_in_set_unknown_bird(test_db: Database, new_bird: Bird):
    """Test adding a bird not in birds table"""
    db = test_db
    unknwon_bird_name = new_bird.en
    set_name = 'test'
    
    all_set_lst = db.list_all_sets()
    all_birds_lst = db.list_all_birds()
    assert unknwon_bird_name not in all_birds_lst
    assert set_name in all_set_lst
    
    response = db.add_bird_in_set(bird_name=unknwon_bird_name, set_name=set_name)
    assert response == False

    # check that not added to database
    all_birds_lst_after = db.list_all_birds()
    assert unknwon_bird_name not in all_birds_lst_after


def test_add_bird_in_set_unknown_set(test_db: Database, new_set: UserSet, test_bird_names: list):
    """Test adding to a non existing set"""
    db = test_db
    unknwon_set_name = new_set.set_name
    bird_name = test_bird_names[-1]
    
    all_set_lst = db.list_all_sets()
    all_birds_lst = db.list_all_birds()
    assert unknwon_set_name not in all_set_lst
    assert bird_name in all_birds_lst
    
    response = db.add_bird_in_set(bird_name=bird_name, set_name=unknwon_set_name)
    assert response == False

    # check that not added to database
    all_set_lst_after = db.list_all_sets()
    assert unknwon_set_name not in all_set_lst_after


def test_add_bird_in_set_if_already_in_set(test_db: Database):
    """Test case if the bird is already in set"""
    db = test_db
    target_set = 'test'

    set_before = db.db.query(UserSet).filter(UserSet.set_name == target_set).first()
    birds_in_set = [bird_obj.en for bird_obj in set_before.birds]
    assert len(birds_in_set) > 0
    bird_name = birds_in_set[0]  # select a bird already present in the set

    response = db.add_bird_in_set(bird_name=bird_name, set_name=target_set)
    assert response == True


def test_add_bird_in_set_all_ok(test_db: Database, test_bird_names: list):
    """Test adding a bird to a set"""
    db = test_db
    target_set = 'test'
    bird_name = test_bird_names[-1]

    set_before = db.db.query(UserSet).filter(UserSet.set_name == target_set).first()
    bird_before = db.db.query(Bird).filter(Bird.en == bird_name).first()
    nb_birds_before = len(set_before.birds)
    assert set_before not in bird_before.user_sets

    response = db.add_bird_in_set(bird_name=bird_name, set_name=target_set)
    assert response == True

    # check that database was changed
    set_after = db.db.query(UserSet).filter(UserSet.set_name == target_set).first()
    bird_after = db.db.query(Bird).filter(Bird.en == bird_name).first()
    nb_birds_after = len(set_after.birds)
    assert nb_birds_after == nb_birds_before + 1
    assert set_after in bird_after.user_sets


def test_remove_bird_from_set_unknown_bird(test_db: Database, new_bird: Bird):
    """Test removing a bird not present in set"""
    db = test_db
    set_name = 'test'
    bird_name = new_bird.en
    set_before = db.db.query(UserSet).filter(UserSet.set_name == set_name).first()
    birds_in_set = [bird_obj.en for bird_obj in set_before.birds]
    assert bird_name not in birds_in_set

    response = db.remove_bird_from_set(bird_name=bird_name, set_name=set_name)
    assert response == False


def test_remove_bird_from_set_unknown_set(test_db: Database, new_set: UserSet):
    """Test removing a bird not present in set"""
    db = test_db
    set_name = new_set.set_name
    bird_name = "Olivaceous Saltator"
    set_lst = db.list_all_sets()

    assert bird_name in db.list_all_birds()
    assert set_name not in set_lst
    response = db.remove_bird_from_set(bird_name=bird_name, set_name=set_name)
    assert response == False


def test_remove_bird_from_set_all_ok(test_db: Database):
    """Test removing a bird not present in set"""
    db = test_db
    set_name = 'test'
    set_before = db.db.query(UserSet).filter(UserSet.set_name == set_name).first()
    bird_before = set_before.birds[0] # take a bird present in set
    bird_name = bird_before.en  
    response = db.remove_bird_from_set(bird_name=bird_name, set_name=set_name)
    assert response == True

    # check that db was changed
    set_after = db.db.query(UserSet).filter(UserSet.set_name == set_name).first()
    birds_after = db.db.query(Bird).filter(Bird.en == bird_name).first()

    bird_names_in_set = [bird_obj.en for bird_obj in set_after.birds]
    assert bird_name not in bird_names_in_set

    set_names_in_bird = [set_obj.set_name for set_obj in birds_after.user_sets]
    assert set_name not in set_names_in_bird


def test_get_random_bird_from_set_unknown_set(empty_tables: Database, new_set: UserSet):
    db = empty_tables
    set_name = new_set.set_name
    assert set_name not in db.list_all_sets()
    random_bird = db.get_random_bird_from_set(set_name)
    assert random_bird is None


def test_get_random_bird_from_set_empty_set(test_db: Database):
    db = test_db
    set_name = 'empty_set'
    assert set_name in db.list_all_sets()
    random_bird = db.get_random_bird_from_set(set_name)
    assert random_bird is None


def test_get_random_bird_from_set(test_db: Database):
    """
    Test that random selection return proper data
    This doesn't test the randomness
    """
    db = test_db
    set_name = 'test_multiple_birds'
    set_before = db.db.query(UserSet).filter(UserSet.set_name == set_name).first()
    assert set_before is not None  # check that set exists
    assert len(set_before.birds) > 1  # check that there are multiple birds
    
    random_bird = db.get_random_bird_from_set(set_name=set_name)
    assert isinstance(random_bird, Bird)
    assert random_bird in set_before.birds


def test_get_bird_wrong_bird(test_db: Database, new_bird:Bird):
    db = test_db
    bird_name = new_bird.en
    bird_obj = db.get_bird(bird_name=bird_name)
    assert bird_obj is None


def test_get_bird(test_db: Database, test_bird_names:list):
    db = test_db
    bird_name = test_bird_names[0]
    bird_obj = db.get_bird(bird_name=bird_name)
    assert bird_obj is not None
    assert isinstance(bird_obj, Bird)
    assert bird_obj.en == bird_name


def test_list_birds_in_set_unknown_set(test_db: Database, new_set: UserSet):
    db = test_db
    set_name = new_set.set_name
    bird_lst = db.list_birds_in_set(set_name=set_name)
    assert bird_lst is None


def test_list_birds_in_set_empty_set(test_db: Database):
    db = test_db
    set_name = 'empty_set'
    bird_lst = db.list_birds_in_set(set_name=set_name)
    assert isinstance(bird_lst, list)
    assert len(bird_lst) == 0


def test_list_birds_in_set_unknown_set(test_db: Database, test_bird_names: list):
    db = test_db
    set_name = 'test'
    expected_bird_lst = ["Olivaceous Saltator"] 
    bird_lst = db.list_birds_in_set(set_name=set_name)
    assert isinstance(bird_lst, list)
    assert bird_lst == expected_bird_lst