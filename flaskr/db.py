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
    db_file_path: str


    def init_db(self) -> None:
        self.engine = create_engine(f"sqlite+pysqlite:///{self.db_file_path}")
        self.db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))


    def close_db(self) -> None:
        if self.engine:
            self.engine.close()


    def set_id_from_name(self, set_name: str) -> int|None:
        # Return the id associanted to a given set name
        # Returns None if the set doesn't exists
        query = text(
            "SELECT id, set_name FROM user_sets"
        )
        set_id = None
        results = self.db.execute(query)
        for row in results:
            if row.set_name == set_name:
                set_id = row.id
        return set_id


    def list_all_sets(self) -> list[str]:
        # Return a list of all existing set names
        query = text(
            f"SELECT set_name FROM user_sets" 
        )
        results = self.db.execute(query)
        set_lst = [row.set_name for row in results]
        return set_lst
        

    def bird_id_from_name(self, bird_name: str) -> int|None:
        """
        Return the id of a bird from its name or None if bird doesn't exists
        In case of multiple matches, return only the first match
        """
        
        bird_id = None
        query = text(
            f"SELECT id FROM birds WHERE en == {bird_name} LIMIT 1"
        )
        results = self.db.execute(query)
        bird_id = results.first().id
        return bird_id


    def list_birds_in_set(self, set_name: str|None=None) -> list[str]:
        # Returns a list of all birds presetn in a given set.
        # If set doesn't exist return an empty list
        # If None, return all birds in 'birds' table
        bird_lst = []

        if set_name is None:
            bird_lst = get_all_birds()
        else:
            set_id = get_user_set_id(set_name)
        
            if set_id is None:
                return []
            
            query = text(
                f"""
                SELECT birds.bird_name as name FROM birds_in_set set
                LEFT JOIN birds on birds.id == set.bird_id
                WHERE set.set_id = {set_id} 
                """
            )
            results = self.db.execute(query)
            bird_lst = [row.name for row in results]
        return bird_lst


    def delete_user_set(self, set_name:str) -> bool:
        """
        Add a user set in the database.
        Returns True if created successfully, False otherwise
        """
        success = True
        user_set_id = self.set_id_from_name(set_name)
        
        # only delete if set exists
        if user_set_id is None:
            return False

        delete_set_content_query = text(
            f"DELETE FROM birds_in_set WHERE set_id == '{user_set_id}'"
        )

        delete_set_query = text(
            f"DELETE FROM user_sets WHERE id == '{user_set_id}'"
        )

        try:
            with self.engine.connect() as conn:
                conn.execute(delete_set_content_query)
                conn.execute(delete_set_query)
                conn.commit()
        except:
            success = False
        return success


    def create_user_set(self, set_name:str) -> bool:
        """
        create a user set in database
        Returns True if successful, False otherwise
        """
        success = True

        create_set_query = text(
            f"INSERT INTO user_sets (set_name) VALUES ('{set_name}')"
        )

        try:
            with self.engine.connect() as conn:
                conn.execute(create_set_query)
                conn.commit()
        except:
            success = False
        return success
    

    def add_bird_in_set(self, bird_name:str, set_name:str) -> bool:
        """
        add a bird to a given user set
        Returns True if successful, False otherwise
        """
        success = True
        set_id = self.set_id_from_name(set_name)
        bird_id = self.bird_id_from_name(bird_name)
        # only add if both set and bird exists
        if set_id is None or bird_id is None:
            return False

        query = text(
            f"INSERT INTO birds_in_set (bird_id, set_id) VALUES ('{bird_id}', '{set_id}')"
        )

        try:
            with self.engine.connect() as conn:
                conn.execute(query)
                conn.commit()
        except:
            success = False
        return success



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


# def get_engine() -> 'sqlalchemy.engine.Engine':
#     """ Create a single engine per request"""
#     if 'db_engine' not in g:
#         g.db_engine = create_engine(f"sqlite+pysqlite:///{current_app.config['DB_FILE']}")
#     return g.db_engine


# def connect_to_database() -> 'sqlalchemy.orm.scoped_session':
#     """ Return a thread safe session connected to database"""
#     engine = get_engine()
#     Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     return scoped_session(Session)

def connect_to_database() -> Database:
    """ Create a Datbase object and connect it to the database"""
    db = Database(db_file_path=current_app.config['DB_FILE'])
    db.init_db()
    return db


def get_db() -> Database:
    # return the same connection to database within a request
    if 'db' not in g:
        g.db = connect_to_database()
    return g.db


def close_db(e=None):
    """
    Close database session at the end of app run
    e argument is required, it throws an error if not present.
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()


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




