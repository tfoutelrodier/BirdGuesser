import logging
import random

from dataclasses import dataclass
from flask import g, current_app
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine, Row

from .db_models import Bird, UserSet


####
# Database class handling all CRUD interactions with the database
####

@dataclass
class Database():
    engine: Engine

    def __post_init__(self) -> None:
        self.db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))


    def close_db(self) -> None:
        if self.db:
            self.db.remove()
        if self.engine:
            self.engine.dispose()


    def commit_changes(self):
        # commit changes to the database
        self.db.commit()


    def list_all_sets(self) -> list[str]:
        # Return a list of all existing set names

        inspector = inspect(self.engine)
        if not inspector.has_table(UserSet.__tablename__):
            logging.error(f"table '{UserSet.__tablename__}' doesn't exist, returning empty list")
            return []
        results = self.db.query(UserSet.set_name).all()
        print(results)
        if results:
            set_lst = [row.set_name for row in results]
        else:
            set_lst = []
        logging.debug(f"db.list_all_set returns a {type(set_lst)}")
        return set_lst


    # def bird_name_from_id(self, bird_id:int) -> str|None:
    #     """
    #     Return a bird name from its birds table id
    #     """
    #     result = self.db.query(Bird.en).filter(Bird.id == bird_id).first()
    #     if result:
    #         return result.en
    #     else:
    #         return None


    def list_all_birds(self) -> list[str]:
        """
        bird names are held within the 'en' column in databse
        """
        inspector = inspect(self.engine)
        if not inspector.has_table(Bird.__tablename__):
            logging.error(f"table '{Bird.__tablename__}' doesn't exist, returning empty list")
            return []
        # Returns a list of all birds in the birds table
        all_birds: list[Row] = self.db.query(Bird.en).all()
        bird_name_lst = [row.en for row in all_birds]
        return bird_name_lst


    def list_birds_in_set(self, set_name: str|None=None) -> list[str]|None:
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
                return None

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
                self.commit_changes()
                logging.info(f"Set '{set_name}' deleted")
            return True
        except Exception as e:
            logging.error(f"Error when deleting set '{set_name}': {e}")
            return False


    def create_user_set(self, set_name:str) -> UserSet:
        """
        create a user set in database
        Returns the new set object or the existing set if the name is already taken 
        """
        existing_set = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()
        if existing_set:
            logging.info(f"${set_name} already exist, skipping creation")
            return existing_set
        
        new_set = UserSet(set_name=set_name)
        self.db.add(new_set)
        self.commit_changes()
        logging.info(f"Create user set with name {set_name}")
        return new_set
    

    def add_bird_in_set(self, bird_name:str, set_name:str) -> bool:
        """
        add a bird to a given user set
        Returns True if successful, False otherwise
        """
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
            self.commit_changes()
            logging.info(f"{bird_name} was added to {set_name}")
        return True


    def remove_bird_from_set(self, bird_name: str, set_name: str) -> bool:
        """
        remove a bird from a given user set
        Returns True if successful, False otherwise
        """
        bird = self.db.query(Bird).filter(Bird.en == bird_name).first()
        user_set = self.db.query(UserSet).filter(UserSet.set_name == set_name).first()

        if not bird:
            logging.error(f"Bird name {bird_name} was not found")
            return False
        elif not user_set:
            logging.error(f"Set {set_name} was not found")
            return False
        
        if bird not in user_set.birds:
            logging.info(f"{bird_name} is not in {set_name}. Skipping...")
        else:
            # the birds attribute created with relationship behaves similarly to a list
            user_set.birds.remove(bird)
            self.commit_changes()
            logging.info(f"{bird_name} was added to {set_name}")
        return True


    def get_random_bird_from_set(self, set_name:str|None) -> Bird | None:
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


def get_engine(db_file:str|None=None) -> Engine:
    """
    Create a single engine per request
    Will look for app config database by default
    """
    if db_file is None:
        db_file = current_app.config['DB_FILE']

    if 'db_engine' not in g:
        g.db_engine = create_engine(f"sqlite+pysqlite:///{db_file}")
    return g.db_engine


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
