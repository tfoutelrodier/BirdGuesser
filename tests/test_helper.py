
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_store_dataframe_in_session(app) -> None:
    """Test if can store and a df in session object as a str."""
    test_df = pd.DataFrame(
        [
            {'test_col':'this_is_a_test'}
        ]
    )
    with app.test_request_context():
        # import within this with statement for session object to be defined
        from flaskr.helper import store_dataframe_in_session
        from flask import session
        store_dataframe_in_session(df=test_df, key="test")
        print(test_df)
        print(session['test'])
        assert 'test' in session
        assert type(session['test']) is str


def test_load_dataframe_from_session(app) -> None:
    ''' Test is can store a dataframe stored using store_dataframe_in_session()'''
    test_df = pd.DataFrame(
        [
            {'test_col':'this_is_a_test'}
        ]
    )
    with app.test_request_context():
        # import within this with statement for session object to be defined
        from flaskr.helper import store_dataframe_in_session, load_df_from_session
        from flask import session
        store_dataframe_in_session(df=test_df, key="test")
        assert 'test' in session
        recovered_df = load_df_from_session('test')
        print(recovered_df)
        pd.testing.assert_frame_equal(test_df, recovered_df)
        

def test_json2df():
    from flaskr.helper import json2df
    test_df = pd.DataFrame(
    [
        {'test_col':'this_is_a_test'}
    ]
    )
    test_str = '{"columns":["test_col"],"index":[0],"data":[["this_is_a_test"]]}'
    pd.testing.assert_frame_equal(test_df, json2df(test_str))
    

def test_df2json():
    from flaskr.helper import df2json
    test_df = pd.DataFrame(
    [
        {'test_col':'this_is_a_test'}
    ]
    )
    test_str = '{"columns":["test_col"],"index":[0],"data":[["this_is_a_test"]]}'
    assert df2json(test_df) == test_str
