import csv
import logging
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine import Engine

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)

from flaskr.db_models import Base


def create_commom_bird_set(
    engine:Engine,
    metadata_obj:MetaData
                          ) -> None:
    """
    Create a 'commom birds' dataset in the database
    Add data to both 'user_sets' and 'birds_in_set' table in accordance
    """
    common_bird_names = [
        'Common Chaffinch',
        'Common Wood Pigeon',
        'Dunnock',
        'Common Blackbird',
        'Eurasian Blackcap',
        'Eurasian Bullfinch',
        'Eurasian Collared Dove',
        'Western Jackdaw',
        'Eurasian Jay',
        'Eurasian Magpie',
        'Eurasian Nuthatch',
        'Eurasian Siskin',
        'Eurasian Wren',
        'European Greenfinch',
        'European Goldfinch',
        'European Robin',
        'Common Starling',
        'European Green Woodpecker',
        'Great Spotted Woodpecker',
        'Hawfinch',
        "House Sparrow",
        "Eurasian Blue Tit",
        "Coal Tit",
        "European Crested Tit",
        "Great Tit",
        "Long-tailed Tit",
        "Marsh Tit",
        "Willow Tit",
        "Yellowhammer"
    ]

    user_set_table = metadata_obj.tables['user_sets']
    birds_in_sets_table = metadata_obj.tables['birds_in_set']

    # Create the set
    logging.info("Creating 'common_birds' set")
    set_data = [{'set_name':'common_birds'}]
    with engine.connect() as conn:
        insert_data = user_set_table.insert().values(set_data)
        conn.execute(insert_data)
        conn.commit()

    # Fill the set
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    set_id_query = text(
        "SELECT id from user_sets WHERE set_name = 'common_birds'"
    )
    common_bird_set_id = db_session.execute(set_id_query).first().id

    bird_data_lst = []
    for bird_name in common_bird_names:
        bird_name_lower = bird_name.lower()
        query = text(
                f"SELECT id FROM birds WHERE en = '{bird_name_lower}'"
        )
        response = db_session.execute(query)
        try:
            bird_id = response.first().id
        except:
            logging.error(f"Couldn't find {bird_name_lower} in birds table")
            raise KeyError(f"Couldn't find {bird_name_lower} in birds table")

        row_dict = {
            'bird_id':bird_id,
            'set_id':common_bird_set_id
        }
        bird_data_lst.append(row_dict)
    
    db_session.close()

    logging.info("Loading birds data in birds_in_set table for common birds")
    with engine.connect() as conn:
        insert_data = birds_in_sets_table.insert().values(bird_data_lst)
        conn.execute(insert_data)
        conn.commit()


def load_bird_data_in_database(
        data_file:str,
        data_file_separator:str,
        metadata_obj:MetaData,
        engine:Engine
                                ) -> None:
    """
    Load all birds data into the birds table
    """
    birds_table = metadata_obj.tables['birds']

    # load bird data into a list of dict to insert efficiently into the birds table
    birds_data = []
    with open(data_file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=data_file_separator)
            
        # Add each row to our data list
        for row in csv_reader:
            birds_data.append(row)

    # Make sure that there is no '-' in dict key    
    keys_to_rename = []
    for key in birds_data[0]:
        if key != key.replace('-', '_'):
            keys_to_rename.append(key)
    
    if len(keys_to_rename) > 0:
        logging.info('replacing some keys to avoid problematic character in col names')
        for key in keys_to_rename:
            for row_dict in birds_data:
                row_dict[key.replace('-','_')] = row_dict.pop(key)

    # check that all cols have the required keys
    logging.info("Checking that all entries have the required colums")
    for row_dict in birds_data:
        for key in ['id', 'gen', 'sp', 'en', 'lat', 'lng', 'url', 'file', 'file_name']:
            if key not in row_dict:
                logging.error(f"Expected key {key} not found for data {row_dict}")
        
        # put english name in lower case to make it easier to search
        row_dict['en'] = row_dict['en'].lower()

    # Write the data
    logging.info('inserting data into birds table')
    with engine.connect() as conn:
        insert_data = birds_table.insert().values(birds_data)
        conn.execute(insert_data)
        conn.commit()
    logging.info('All data were loaded in the birds table')


def create_database(
        db_file:str,
        data_file: str,
        data_file_separator: str,
        ):
    """
    Create the database with empty tables
    Load the birds dataabse with all bird data
    """
    logging.info(f'Logging to database {db_file}')
    engine = create_engine(f"sqlite+pysqlite:///{db_file}", echo=True)

    try:
        Base.metadata.create_all(engine)
        logging.info("Database table successfully initialized")
    except Exception as e:
        logging.error(f"Something happened during database table set up: {e}")

    load_bird_data_in_database(data_file, data_file_separator, Base.metadata, engine)

    create_commom_bird_set(engine, Base.metadata)


if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    # db_sql_file = os.path.join(script_dir, 'birds_schema.sql')
    database_file = os.path.join(script_dir, 'birds_db.db')

    bird_data_file = os.path.join(script_dir, 'french_bird_data.csv')
    bird_data_file_sep = "|"

    if not os.path.isfile(database_file):
        print("Creating the database and loading bird data")
        create_database(
            db_file=database_file,
            data_file=bird_data_file,
            data_file_separator=bird_data_file_sep
                       )
    else:
        print("Database file already exists, exiting")
