'''
Various misc helper functions
'''
from io import StringIO

import pandas as pd
from flask import session, current_app


def store_dataframe_in_session(df: pd.DataFrame, key: str) -> None:
    """Store a pandas DataFrame in the session as a string"""
    json_string = df.to_json(orient='split')
    session[key] = json_string
    current_app.logger.info(f"Stored df in session with key {key}")


def load_df_from_session(key: str) -> pd.DataFrame:
    """
        Load a dataframe stored as a dict in session object
        Returns a dataframe object
    """
    if key not in session:
        current_app.logger.error(f"key {key} was not found in session")
        raise KeyError(f"key {key} was not found in session")
    
    current_app.logger.info(f"Retrieved data form session key {key}")
    return pd.read_json(StringIO(session[key]), orient='split')


def df2json(df: pd.DataFrame) -> str:
    """
        Returns the json string corresponding to a dataframe
        This string can be loaded in session object
    """
    return df.to_json(orient='split')


def json2df(json_str: str) -> pd.DataFrame:
    """
        Returns the datafarme corresponding to a json string
    """
    return pd.read_json(StringIO(json_str), orient='split')