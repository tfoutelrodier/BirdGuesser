'''
Various misc helper functions
'''
from io import StringIO

import pandas as pd
from flask import session


def store_dataframe_in_session(df: pd.DataFrame, key: str) -> None:
    """Store a pandas DataFrame in the session as a string"""
    buffer = StringIO()
    df.to_json(buffer, orient='split')
    session[key] = buffer.getvalue()