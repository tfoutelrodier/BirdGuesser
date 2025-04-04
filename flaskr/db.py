import pathlib
import csv
import logging
import random

from dataclasses import dataclass
import pandas as pd
from flask import app, g, current_app
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.engine import Engine, Row

from .db_models import Bird, UserSet


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


####
# SQLalchemy ORM based objects
####

@dataclass
class Database():
    engine: Engine

    def __post_init__(self) -> None:
        self.db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))


    def close_db(self) -> None:
        if self.engine:
            self.engine.dispose()


    # def set_id_from_name(self, set_name: str) -> int|None:
    #     # Return the id associanted to a given set name
    #     # Returns None if the set doesn't exists
    #     query = text(
    #         "SELECT id, set_name FROM user_sets"
    #     )
    #     set_id = None
    #     results = self.db.execute(query)
    #     for row in results:
    #         if row.set_name == set_name:
    #             set_id = row.id
    #     return set_id


    def list_all_sets(self) -> list[str]:
        # Return a list of all existing set names
        query = text(
            f"SELECT set_name FROM user_sets" 
        )
        results = self.db.execute(query)
        set_lst = [row.set_name for row in results]
        return set_lst
        

    # def bird_id_from_name(self, bird_name: str) -> int|None:
    #     """
    #     Return the id of a bird from its name or None if bird doesn't exists
    #     In case of multiple matches, return only the first match
    #     """
        
    #     bird_id = None
    #     query = text(
    #         f"SELECT id FROM birds WHERE en == {bird_name} LIMIT 1"
    #     )
    #     results = self.db.execute(query)
    #     bird_id = results.first().id
    #     return bird_id


    def bird_name_from_id(self, bird_id:int) -> str|None:
        """
        Return a bird name from its birds table id
        """
        result = self.db.query(Bird.en).filter(Bird.id == bird_id).first()
        if result:
            return result.en
        else:
            return None


    def list_all_birds(self) -> list[str]:
        """
        bird names are held within the 'en' column in databse
        """
        # Returns a list of all birds in the birds table
        all_birds: list[Row] = self.db.query(Bird.en).all()
        bird_name_lst = [row.en for row in all_birds]
        return bird_name_lst


    def list_birds_in_set(self, set_name: str|None=None) -> list[str]:
        # Returns a list of all birds presetn in a given set.
        # If set doesn't exist return an empty list
        # If None, return all birds in 'birds' table
        bird_lst = []
        if set_name is None:
            logging.info("No set name provided, loading all birds")
            bird_lst = self.list_all_birds()
        else:
            user_set = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()
            if not user_set:
                logging.error(f"Set '{set_name}' was not found")
                return []

            bird_obj_lst = user_set.birds
            bird_lst = [bird.en for bird in bird_obj_lst]
            logging.info(f"Loaded birds from '{set_name}'")
        
        return bird_lst


    def delete_user_set(self, set_name:str) -> bool:
        """
        Remove a user set from database.
        Returns True if deleted of if set doesn't exist, False otherwise
        """
        try:
            set_to_delete = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()

            if not set_to_delete:
                logging.info(f"Set '{set_name}' not found. skipping delete")
            else:
                self.db.delete(set_to_delete)
                logging.info(f"Set '{set_name}' deleted")
            return True
        except Exception as e:
            logging.error(f"Error when deleting set '{set_name}': {e}")
            return False
        # user_set_id = self.set_id_from_name(set_name)
        
        # # only delete if set exists
        # if user_set_id is None:
        #     return False

        # delete_set_content_query = text(
        #     f"DELETE FROM birds_in_set WHERE set_id == '{user_set_id}'"
        # )

        # delete_set_query = text(
        #     f"DELETE FROM user_sets WHERE id == '{user_set_id}'"
        # )

        # try:
        #     with self.engine.connect() as conn:
        #         conn.execute(delete_set_content_query)
        #         conn.execute(delete_set_query)
        #         conn.commit()
        # except:
        #     success = False
        # return success


    def create_user_set(self, set_name:str) -> UserSet:
        """
        create a user set in database
        Returns the new set object or the existing set if the name is already taken 
        """

        # create_set_query = text(
        #     f"INSERT INTO user_sets (set_name) VALUES ('{set_name}')"
        # )
        
        existing_set = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()
        if existing_set:
            logging.info(f"${set_name} already exist, skipping creation")
            return existing_set
        
        new_set = UserSet(set_name=set_name)
        self.db.add(new_set)
        logging.info(f"Create user set with name {set_name}")
        return new_set
    

    def add_bird_in_set(self, bird_name:str, set_name:str) -> bool:
        """
        add a bird to a given user set
        Returns True if successful, False otherwise
        """

        # query = text(
        #     f"INSERT INTO birds_in_set (bird_id, set_id) VALUES ('{bird_id}', '{set_id}')"
        # )

        bird = self.db.query(Bird).filter(Bird.en == bird_name).first()
        user_set = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()

        if not bird:
            logging.error(f"Bird name {bird_name} was not found")
            return False
        elif not user_set:
            logging.error(f"Set {set_name} was not found")
            return False
        
        if bird in user_set.birds:
            logging.info(f"{bird_name} is already in {set_name}. Skipping...")
        else:
            # the birds attribute created with relationship behaves similarly to a list
            user_set.birds.append(bird)
            logging.info(f"{bird_name} was added to {set_name}")
        return True


    def get_random_bird_from_set(self, set_name:str) -> Bird | None:
        """
        Select a random bird from a user set. 
        Is set is None, select a random bird from the birds table instead
        Returns None if no bird was found
        """
        user_set = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()
        if user_set is None:
            logging.error(f"User set {set_name} not found ")
            return None
        elif not user_set.birds:
            logging.error(f'No bird in set {set_name}')
            return None

        random_bird = random.choice(user_set.birds)
        return random_bird
    

    def get_bird(self, bird_name: str) -> Bird | None:
        """
        Returns a Bird object holding all bird data.
        Returns None if no bird with this name was found
        """
        bird = self.db.query(Bird).filter(Bird.en == bird_name).first()
        return bird


####
# SQL function
####


def get_engine(db_file:str|None) -> Engine:
    """
    Create a single engine per request
    Will look for app config database by default
    """
    if db_file is None:
        db_file = current_app.config['DB_FILE']

    if 'db_engine' not in g:
        g.db_engine = create_engine(f"sqlite+pysqlite:///{db_file}")
    return g.db_engine


# def connect_to_database() -> 'sqlalchemy.orm.scoped_session':
#     """ Return a thread safe session connected to database"""
#     engine = get_engine()
#     Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     return scoped_session(Session)

def connect_to_database(file:str|None=None) -> Database:
    """
    Create a Datbase object and connect it to the database
    By default, read app config to look for db file to connect to
    """
    if file is None:
        file = current_app.config['DB_FILE']
    engine = get_engine(file)
    return Database(engine)


def get_db() -> Database:
    # return the same connection to database within a request
    if 'db' not in g:
        g.db = connect_to_database()
    return g.db


def close_db(e=None) -> None:
    """
    Close database session at the end of app run
    e argument is required, it throws an error if not present.
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close_db()


# def get_user_set_id(set_name:str) -> int|None:
#     """
#     Returns the id of the correspondiong set
#     Returns None if the set doesn't exists
#     """
#     db = get_db()
#     query = text(
#         "SELECT id, set_name FROM user_sets"
#     )
#     set_id = None
#     results = db.execute(query)
#     for row in results:
#         if row.set_name == set_name:
#             set_id = row.id
#     return set_id


# def get_bird_sound_url_from_name(bird_name: str, table_name: str = 'birds') -> str|None:
#     """
#     Retrieve the sound url from a bird name.
#     If multiple records match the name, return one at random 
#     """
#     db = get_db()
#     query = text(
#         f"SELECT file FROM {table_name} WHERE en = {bird_name} ORDER BY RANDOM() LIMIT 1" 
#     )
#     result = db.execute(query)
    
#     if result:
#         url = result.first().file
#     else:
#         url = None
#     return url


# def select_bird_from_table(table_name: str='birds', random: bool=False) -> tuple[str|None]:
#     """
#     Select a bird record from either all birds or from a subset table
#     Return the corresponding name
#     """
#     db = get_db()
#     query_str = f"SELECT id, en, file FROM {table_name}"
#     if random:
#         query_str += " ORDER BY RANDOM()"
#     else:
#         query_str += " LIMIT 1"
#     query = text(query_str)

#     result = db.execute(query)
    
#     if result:
#         result_dict = result.first()._asdict()
#         bird_name = result_dict.get('en')
#         bird_id = result_dict.get('id')
#         sound_url = result_dict.get('file', None)
#     else:
#         bird_name = None
#         sound_url = None
#         bird_id = None

#     return (bird_id, bird_name, sound_url)


# def get_all_birds() -> list[str]:
#     """
#     Return a a list of all bird names present in the birds table 
#     """
#     db = get_db()
#     query = text(
#         f"SELECT en FROM birds" 
#     )
#     results = db.execute(query)
    
#     bird_name_lst = []
#     if results:
#         for row in results:
#             bird_name_lst.append(row.en)
#     return bird_name_lst


# def create_user_set(set_name: str) -> str:
#     """
#     Create a new set in the user_sets table
#     Return this set id
#     """
#     db = get_db()

#     new_set = UserSet(set_name=set_name)
#     db.add(new_set)
#     db.commit()
#     logging.info(f"Created user set {new_set.set_name} with id {new_set.id}")
#     return new_set.id


# def get_bird_id_from_name(bird_name: str) -> int:
#     """
#     Return the id of a bird from its name
#     In case of multiple matches, return only the first match
#     """
#     db = get_db()

#     query = text(
#         f"SELECT id FROM birds WHERE en == {bird_name} LIMIT 1"
#     )
#     results = db.execute(query)
#     bird_id = results.first().id
#     return bird_id


# def add_bird_to_user_set(bird_name: str, set_name: str):
#     """
#     Add bird to dataset
#     create_dataset if needed
#     """
#     db = get_db()
#     set_id = get_user_set_id(set_name)
    
#     # create set and get it's id if not existing
#     if set_id is None:
#         set_id = create_user_set(set_name)

#     bird_id = get_bird_id_from_name(bird_name)

#     new_bird_in_set = BirdInSet(
#         set_id=set_id,
#         bird_id=bird_id
#     )
    
#     db.add(new_bird_in_set)
#     db.commit()
#     logging.info(f"Added {new_bird_in_set.bird_id} to set {new_bird_in_set.set_id} with id {new_bird_in_set.id}")


# def get_birds_from_set(set_name: str|None) -> list[str]:
#     """
#     Given a user bird set name, return a list of all bird names in this set
#     Returns an empty list if the set doesn't exist
#     """
#     db = get_db()
#     bird_lst = []
#     if set_name is None:
#         bird_lst = get_all_birds()
#     else:
#         set_id = get_user_set_id(set_name)
    
#         if set_id is None:
#             return []
        
#         query = text(
#             f"""
#             SELECT birds.bird_name as name FROM birds_in_set set
#             LEFT JOIN birds on birds.id == set.bird_id
#             WHERE set.set_id = {set_id} 
#             """
#         )
#         results = db.execute(query)
#         bird_lst = [row.name for row in results]
#     return bird_lst




