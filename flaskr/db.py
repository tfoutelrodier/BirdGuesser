import pathlib
import csv
import logging
import random

import pandas as pd
from flask import app, g, current_app
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


def load_random_rows_from_csv(filepath:pathlib.Path, nb_rows=100) -> pd.DataFrame:
    # avoid loading all the file at once
    sample = []
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        header = next(reader)  # Read and store the header
        
        for i, row in enumerate(reader, start=1):
            if len(sample) < nb_rows:
                sample.append(row)  # Fill the reservoir
            else:
                r = random.randint(0, i)
                if r < nb_rows:
                    sample[r] = row  # Replace an existing row

    return pd.DataFrame(sample, columns=header)


def load_bird_names(filepath: pathlib.Path) -> list[str]:
    # return all bird names (english names) as a list
    bird_names = []
    name_index = None
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        header = next(reader)  # Read header
        
        for i, col_name in enumerate(header):
            if col_name == 'en':
                name_index = i
        if name_index is not None:
            for _, row in enumerate(reader, start=1):
                bird_names.append(row[name_index])
    
    return bird_names


def get_bird_data(filepath: pathlib.Path, bird_names: list[str]) -> pd.DataFrame:
    # returns a dataframe with all data from a list of bird names
    # input names should have a match in the 'en' column of the data (vernacular names)
    
    # avoid loading all the file at once
    kept_rows = []
    name_index = None

    # sanitize bird names
    bird_names_cleaned = [name.strip().lower() for name in bird_names]

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        header = next(reader)  # Read header
        
        for i, col_name in enumerate(header):
            if col_name == 'en':
                name_index = i
        if name_index is not None:
            for _, row in enumerate(reader, start=1):
                if row[name_index].strip().lower() in bird_names_cleaned:
                    kept_rows.append(row)
    
    return pd.DataFrame(kept_rows, columns=header) 

####
# SQL base object format
####

class UserSet(declarative_base()):
    """
    Represent a bird set from the user_set table
    Useful for creation of new sets
    """
    __tablename__ = 'user_set'
    id = Column(Integer, primary_key=True, autoincrement=True)
    set_name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"bird set: {self.set_name} with id: {self.id}"


class BirdInSet(declarative_base()):
    """
    Represent a new bird in birds database.
    This may not ever be used but there in case
    """
    __tablename__ = 'birds_in_set'
    id = Column(Integer, primary_key=True, autoincrement=True)
    set_id = Column(Integer, nullable=False)
    bird_id = Column(String, nullable=False)

    def __repr__(self):
        return f"bird {self.bird_id} is present in set {self.set_id} with id {self.id}"
    

####
# SQL function
####


def get_engine() -> 'sqlalchemy.engine.Engine':
    """ Create a single engine per request"""
    if 'db_engine' not in g:
        g.engine = create_engine(f"sqlite+pysqlite:///{current_app.config['BIRD_DB']}")
    return g.engine


def connect_to_database() -> 'sqlalchemy.orm.scoped_session':
    """ Return a thread safe session connected to database"""
    engine = get_engine()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return scoped_session(Session)


def get_db() -> 'sqlalchemy.orm.scoped_session':
    # return the same connection to database within a request
    if 'db' not in g:
        g.db = connect_to_database()

    return g.db


def close_db(error=None):
    """Close database session at the end of app run"""
    db_session = g.pop('db_session', None)
    
    if db_session is not None:
        db_session.close()


def get_user_set_id(set_name:str) -> int|None:
    """
    Returns the id of the correspondiong set
    Returns None if the set doesn't exists
    """
    db = get_db()
    query = text(
        "SELECT id, set_name FROM user_sets"
    )
    set_id = None
    results = db.execute(query)
    for row in results:
        if row['set_name'] == set_name:
            set_id = row['id']
    return set_id



def get_bird_sound_url_from_name(bird_name: str, table_name: str = 'birds') -> str|None:
    """
    Retrieve the sound url from a bird name.
    If multiple records match the name, return one at random 
    """
    db = get_db()
    query = text(
        "SELECT file FROM :bird_name WHERE en = :bird_name ORDER BY RANDOM() LIMIT 1" 
    )
    result = db.execute(query, {"table_name":table_name, "bird_name":bird_name})
    
    if result:
        url = result.first()._as_dict()['file']
    else:
        url = None
    return url


def select_bird_from_table(table_name: str='birds', random: bool=False) -> tuple[str|None]:
    """
    Select a bird record from either all birds or from a subset table
    Return the corresponding name
    """
    db = get_db()
    query_str = f"SELECT id, en, file FROM :table_name"
    if random:
        query_str += " ORDER BY RANDOM()"
    else:
        query_str += " LIMIT 1"
    query = text(query_str)

    result = db.execute(query, {"table_name":table_name})
    
    if result:
        result_dict = result.first()._as_dict()
        bird_name = result_dict.get('en')
        bird_id = result_dict.get('id')
        sound_url = result_dict.get('file', None)
    else:
        bird_name = None
        sound_url = None
        bird_id = None

    return (bird_id, bird_name, sound_url)


def get_all_birds() -> list[str]:
    """
    Return a a list of all bird names present in the birds table 
    """
    db = get_db()
    query = text(
        f"SELECT en FROM birds" 
    )
    result = db.execute(query)
    
    bird_name_lst = []
    if result:
        for row in result:
            bird_name_lst.append(row['en'])
    return bird_name_lst


def create_user_set(set_name: str) -> str:
    """
    Create a new set in the user_sets table
    Return this set id
    """
    db = get_db()

    new_set = UserSet(set_name=set_name)
    db.add(new_set)
    db.commit()
    logging.info(f"Created user set {new_set.set_name} with id {new_set.id}")
    return new_set.id


def get_bird_id_from_name(bird_name: str) -> int:
    """
    Return the id of a bird from its name
    In case of multiple matches, return only the first match
    """
    db = get_db()

    query = text(
        "SELECT id FROM birds WHERE en = :bird_name LIMIT 1"
    )
    results = db.execute(query, {'bird_name':bird_name})
    bird_id = results[0]['id']
    return bird_id


def add_bird_to_user_set(bird_name: str, set_name: str):
    """
    Add bird to dataset
    create_dataset if needed
    """
    db = get_db()
    set_exists = False

    set_id = get_user_set_id(set_name)
    
    # create set and get it's id if not existing
    if set_id is None:
        set_id = create_user_set(set_name)

    bird_id = get_bird_id_from_name(bird_name)

    new_bird_in_set = BirdInSet(
        set_id=set_id,
        bird_id=bird_id
    )
    
    db.add(new_bird_in_set)
    db.commit()
    logging.info(f"Added {new_bird_in_set.bird_id} to set {new_bird_in_set.set_id} with id {new_bird_in_set.id}")


def get_birds_from_set(set_name: str) -> list[str]:
    """
    Given a user bird set name, return a list of all bird names in this set
    Returns an empty list if the set doesn't exist
    """
    db = get_db()
    set_id = get_user_set_id(set_name)
    bird_lst = []

    if set_id is None:
        return []
    
    query = text(
        """
        SELECT birds.bird_name as name FROM birds_in_set set
        LEFT JOIN birds on birds.id = set.bird_id
        WHERE set.set_id = :set_id  
        """
    )
    results = db.execute(query, {'set_id':set_id})
    bird_lst = [row['name'] for row in results]
    return bird_lst



