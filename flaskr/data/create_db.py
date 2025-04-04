import csv
import logging
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy import Table, Column, Integer, String, MetaData


def load_bird_data_in_database(
        data_file:str,
        data_file_separator:str,
        metadata_obj:MetaData,
        engine:'sqlalchemy.engine.Engine'
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

    metadata_obj = MetaData()
    # main table with all data from birds
    birds_table = Table(
        'birds',
        metadata_obj,
        Column("id", Integer, primary_key=True, nullable=False),
        Column('gen', String, nullable=False),
        Column('sp', String, nullable=False),
        Column('en', String, nullable=False),
        Column('lat', String, nullable=True),
        Column('lng', String, nullable=True),
        Column('url', String, nullable=False),
        Column('file', String, nullable=False),
        Column('file_name', String, nullable=False),
    )

    # holds all existing user datasets
    user_sets_table = Table(
        'user_sets',
        metadata_obj,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column('set_name', String, nullable=False, unique=True),
    )

    # holds the composition of each dataset
    birds_in_set_table = Table(
        'birds_in_set',
        metadata_obj,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column("set_id", Integer, nullable=False),
        Column('bird_id', Integer, nullable=False),
    )

    logging.info(f'Creating missing tables')
    table_lst = [birds_table, user_sets_table, birds_in_set_table]
    # checkfirst onyl creates tables that don't already exist
    metadata_obj.create_all(engine, tables=table_lst, checkfirst=True)

    # update the metadata
    metadata_obj.reflect(engine)

    load_bird_data_in_database(data_file, data_file_separator, metadata_obj, engine)



if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    # db_sql_file = os.path.join(script_dir, 'birds_schema.sql')
    database_file = os.path.join(script_dir, 'birds_db.db')

    bird_data_file = os.path.join(script_dir, 'french_bird_data.csv')
    bird_data_file_sep = "|"

    if not os.path.isfile(database_file):
        print("Creating the dataabse and loading bird data")
        create_database(
            db_file=database_file,
            data_file=bird_data_file,
            data_file_separator=bird_data_file_sep
                       )
    else:
        print("Database file already exists, exiting")


    # # Store birds data into the database
    # bird_data_df = pd.read_csv(
    #     filepath_or_buffer=bird_data_file,
    #     header=0,
    #     sep=bird_data_file_sep)
    
    # # replace '-' by "_" in file name to adhere to table schema
    # bird_data_df = bird_data_df.rename(columns=lambda x: x.replace('-', '_'))


    # Create the database table if doesn't exists
    # with engine.connect() as conn:
    #     if not engine.dialect.has_table(conn, 'birds'):
            
            
    #         with open(db_sql_file, 'r') as file:
    #             statements = file.read().split('\n\n')
    #             for statement in statements:
    #                 query = text(statement)
    #                 conn.execute(query)
    #                 conn.commit()
    #     else:
    #         print('Table birds already exists')

    

    # insert_query = text("INSERT INTO birds (id, gen, sp, en, lat, lng, url, file, file_name) VALUES (:id, :gen, :sp, :en, :lat, :lng, :url, :file, :file_name)")
    # with engine.connect() as conn:
    #     for index, row in bird_data_df.iterrows(): 
    #         conn.execute(insert_query, row.to_dict())
    #         conn.commit()
