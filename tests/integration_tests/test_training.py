import os
import sys

from flask import Flask
from flask.testing import FlaskClient
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
from flaskr.db_models import Bird
from conftest import setup_mock_db

#####
# Tests
#####


def test_index_get(client: FlaskClient):
    """
    Test GET on default page
    """
    response = client.get('/training/')
    assert response.status_code == 200


def test_get_bird_name_list_success(client: FlaskClient, test_db_dict:dict):
    """
    Test retrieving and passing a bird name list if stored in session.
    """
    bird_lst = test_db_dict['bird_name_list']
    with client.session_transaction() as sess:
        sess['bird_name_list'] = bird_lst
    
    response = client.get("/training/get_bird_name_list")
    assert response.status_code == 200
    assert response.json == bird_lst


def test_get_bird_name_list_not_is_session(client: FlaskClient):
    """
    Test case if bird list is not in session.
    """
    with client.session_transaction() as sess:
        if 'bird_name_list' in sess:
            del sess['bird_name_list']
    
    response = client.get("/training/get_bird_name_list")
    assert response.status_code == 404
    assert "Bird names not loaded in session" in response.text


def test_get_birds_in_set_specific(client, mocker, test_db_dict):
    """
    Test getting birds for a specific set.
    """
    bird_lst = test_db_dict['bird_name_list']
    set_name = test_db_dict['set_name']
    mock_db = setup_mock_db(mocker, __file__,  list_birds_in_set_return=bird_lst)
    
    response = client.get(f"/training/get_birds_in_set/{set_name}")
    assert response.status_code == 200
    assert response.json == bird_lst
    mock_db.list_birds_in_set.assert_called_once_with(set_name)


def test_get_birds_in_set_default(client:FlaskClient, mocker, test_db_dict:dict):
    """
    Test getting all birds when passing no set name.
    """
    bird_lst = test_db_dict['bird_name_list']
    print(bird_lst)
    mock_db = setup_mock_db(mocker, __file__,  list_all_birds_return=bird_lst)
    
    response = client.get(f"/training/get_birds_in_set")
    print(response.get_json())
    assert response.status_code == 200
    assert response.json == bird_lst
    mock_db.list_all_birds.assert_called_once_with()


def test_get_birds_in_set_error_no_set(client, mocker, test_db_dict):
    """
    Test getting all birds when passing no set name.
    """
    set_name = test_db_dict['set_name']
    mock_db = setup_mock_db(mocker, __file__,  list_birds_in_set_return=[])
    response = client.get(f"/training/get_birds_in_set/{set_name}")
    assert response.status_code == 404
    assert "bird set not found" in response.text
    mock_db.list_birds_in_set.assert_called_once_with(set_name)


def test_get_user_sets_no_option(client, mocker, test_db_dict):
    """
    Test returning a user set list by default.
    """
    user_set_lst = [test_db_dict['set_name']]
    mock_db = setup_mock_db(mocker, __file__,  list_all_sets_return=user_set_lst)
    response = client.get(f"/training/get_user_sets")
    assert response.status_code == 200
    assert response.json == user_set_lst
    mock_db.list_all_sets.assert_called_once_with()


def test_get_user_sets_all(client, mocker, test_db_dict):
    """
    Test returning a user set list explicitely.
    """
    user_set_lst = [test_db_dict['set_name']]
    mock_db = setup_mock_db(mocker, __file__,  list_all_sets_return=user_set_lst)
    response = client.get(f"/training/get_user_sets/all")
    assert response.status_code == 200
    assert response.json == user_set_lst
    mock_db.list_all_sets.assert_called_once_with()


def test_get_user_sets_default(app, client, mocker, test_db_dict):
    """
    Test returning the list of default user sets.
    Reads from flask.config.
    """

    user_set_lst = [test_db_dict['set_name']]
    mock_db = setup_mock_db(mocker, __file__)

    # check that app setup is ok
    assert 'DEFAULT_SET_LIST' in app.config
    assert app.config['DEFAULT_SET_LIST'] == ['test']

    # test function
    response = client.get(f"/training/get_user_sets/default")
    assert response.status_code == 200
    assert response.json == user_set_lst


def test_get_user_sets_wrong_option(client, mocker):
    """
    Test error when passing a wrong option.
    """
    mock_db = setup_mock_db(mocker, __file__)
    response = client.get(f"/training/get_user_sets/invalid")
    assert response.status_code == 400
    assert response.json == []


def test_delete_set_success(client, mocker):
    """
    Test that set can be deleted.
    """
    mock_db = setup_mock_db(mocker, __file__,  delete_user_set_return=True)
    response = client.post(f"/training/delete_set/test")
    assert response.status_code == 200


def test_delete_set_error(client, mocker):
    """
    Test set not deleted.
    """
    mock_db = setup_mock_db(mocker, __file__,  delete_user_set_return=False)
    response = client.post(f"/training/delete_set/test")
    assert response.status_code == 404


def test_create_set_success(client, mocker):
    """
    Test creating a set in database.
    """
    mock_db = setup_mock_db(mocker, __file__,  create_user_set_return=True)
    response = client.post(f"/training/create_set/test")
    assert response.status_code == 200


def test_create_set_error(client, mocker):
    """
    Test creating a set in database.
    """
    mock_db = setup_mock_db(mocker, __file__,  create_user_set_return=False)
    response = client.post(f"/training/create_set/test")
    assert response.status_code == 404


def test_add_to_user_set_success(client, mocker):
    """
    Test adding bird to set.
    """
    mock_db = setup_mock_db(mocker, __file__,  add_bird_in_set_return=True)
    response = client.post(f"/training/add_to_user_set/test_set/test_bird")
    assert response.status_code == 200


def test_add_to_user_set_error(client, mocker):
    """
    Test adding bird to set without success.
    """
    mock_db = setup_mock_db(mocker, __file__,  add_bird_in_set_return=False)
    response = client.post(f"/training/add_to_user_set/test_set/test_bird")
    assert response.status_code == 404


def test_remove_bird_from_set_success(client, mocker):
    """
    Test removing bird from set.
    """
    mock_db = setup_mock_db(mocker, __file__,  remove_bird_from_set_return=True)
    response = client.post(f"/training/remove_bird_from_set/test_set/test_bird")
    assert response.status_code == 200


def test_remove_bird_from_set_error(client, mocker):
    """
    Test removing bird from set without success.
    """
    mock_db = setup_mock_db(mocker, __file__,  remove_bird_from_set_return=False)
    response = client.post(f"/training/remove_bird_from_set/test_set/test_bird")
    assert response.status_code == 404


def test_get_bird_song_success(client, mocker, test_db_dict):
    """
    Test getting song from a bird.
    """
    test_bird: Bird = test_db_dict['bird_objects'][0]
    mock_db = setup_mock_db(mocker, __file__,  get_bird_return=test_bird)
    response = client.get(f"/training/get_bird_song/test_bird")
    assert response.status_code == 200
    assert response.json == test_bird.file


def test_get_bird_song_wrong_bird(client, mocker):
    """
    Test if bird not present in database.
    """
    mock_db = setup_mock_db(mocker, __file__,  get_bird_return=None)
    response = client.get(f"/training/get_bird_song/test_bird")
    assert response.status_code == 404


def test_get_bird_song_success(client, mocker, test_db_dict):
    """
    Test if bird has no song link.
    """
    test_bird: Bird = test_db_dict['bird_objects'][0]
    test_bird.file = None  # Set a bird without file
    mock_db = setup_mock_db(mocker, __file__,  get_bird_return=test_bird)
    response = client.get(f"/training/get_bird_song/test_bird")
    assert response.status_code == 404


def test_get_bird_song_wrong_method(client):
    """
    Test with wrong method.
    """
    response = client.post(f"/training/get_bird_song/test_bird")
    assert response.status_code == 405