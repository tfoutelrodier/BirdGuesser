import json
import pathlib
import csv
import random

import sqlite3
import click  # deal with command line options for database setup but not at the moment
from flask import current_app, g
import pandas as pd


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

    df = pd.DataFrame(sample, columns=header)
    
    return df


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














# def records2list_of_dict(rows, data_col_lst):
#     """
#     Converts the result of a .fetchall() request into a list of dict (one per row)
#     Result can be easily passed back to the client as json format
#     """
#     # Convert rows to list of dictionaries
#     data = []
#     for row in rows:
#         row_dict = {}
#         for index, value in enumerate(row):
#             row_dict[data_col_lst[index]] = value 
#         data.append(row_dict)
#     return(data)


# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row

#     return g.db


# def close_db(e=None):
#     """
#     e stands for error in flask (useless atm but standard in closing/teardown functions)
#     """
#     db = g.pop('db', None)

#     if db is not None:
#         db.close()


# def init_db():
#     db = get_db()

#     with current_app.open_resource('birds_schema.sql') as f:
#         db.executescript(f.read().decode('utf-8'))


# def create_profile_table(db, table_name):
#     '''
#     Create a user table that holds just the required data to train on bird song
#     Data is uid, name, song_file_url, song_file_name
#     '''
#     if table_name == 'birds':
#         print("Can't create profile with this name")
#         return
    
#     # Remove previous table if exists
#     sql_command = f"DROP TABLE IF EXISTS {table_name}"
#     db.execute(sql_command)
    
#     # Create table
#     sql_command = f"CREATE TABLE {table_name} ( \
#         uid INTEGER FOREIGN KEY ,\
#         en TEXT NOT NULL,\
#         file TEXT NOT NULL,\
#         file_name TEXT NOT NULL\
#         )"
#     db.execute(sql_command)


# def delete_profile_table(db, table_name):
#     """
#     delete a user profile table in database
#     """
#     if table_name == 'birds':
#         print("Can't delete profile with this name")
#         return
    
#     # Remove previous table if exists
#     sql_command = f"DROP TABLE IF EXISTS {table_name}"
#     db.execute(sql_command)


# def add_to_profile_table(db, table_name, data_dict):
#     """
#     Add data to profile table
#     """
#     if table_name == 'birds':
#         print("Can't delete profile with this name")
#         return
    
#     sql_command = f"\
#     INSERT INTO {table_name} (uid, en, file, file_name)\
#     VALUES ({data_dict['uid']}, {data_dict['en']}, {data_dict['file']}, {data_dict['file_name']});"
#     db.execute(sql_command)


# def request_bird_data(target_value, db, target_table, target_col='en', main_table='birds', data_cols=['uid','en','file','file_name']):
#     '''
#     Request data about a bird
#     For default values has what is required to add a bird to a user set
#     target_value is the bird name
#     target_table is the user set name
#     db is a sqlite3 connection to the database to query
#     '''
#     sql_command = f"INSERT INTO {target_table} (','.join(data_cols))\
#                     SELECT {','.join(data_cols)} FROM {main_table}\
#                     WHERE {target_col} = {target_value}"
#     # Get data as a tuple
#     try:
#         data = db.execute(sql_command)
#     except:
#         print("ERROR when trying to insert {target_value} data into {target_table} user set")
    

# def fill_db(file_path):
#     db = get_db()
#     error_message = None  # return statement to handle error in basic way
    
#     if not file_path.endswith('.json'):
#         error_message = 'ERROR: {file_path} is not a .json'
#         return(error_message)
    
#     # load json file as a df
#     data_df = pd.read_json(file_path)
    
#     # Remove rows not stored in db
#     col_to_drop_lst = [
#         'group',
#         'rmk',
#         'bird-seen',
#         'animal-seen',
#         'playback-used',
#         'temp',
#         'rec',
#         'regnr',
#         'uploaded',
#         'osci',
#         'animal-seen',
#         'playback-used',
#         'temp',
#         'regnr',
#         'auto',
#         'dvc',
#         'mic',
#         'smp']
#     data_df = data_df.drop(columns=col_to_drop_lst)
    
#     float_col_lst = [
#         'lat',
#         'lng']
#     int_col_lst = [
#         'id']
#     jsonify_col_lst = [  # dict of lst to turn into json serialization
#         'sono',
#         'also']
#     data_df[float_col_lst] = data_df[float_col_lst].astype(float)
#     data_df[int_col_lst] = data_df[int_col_lst].astype(int)
    
#     # DROP NA for lat lon col
#     # This is an ad hoc fix take care of that before when creating the file to import
#     data_df = data_df.dropna(subset=['lat','lng'])

#     # change col names to avoid '-'
#     # Replace '-' with '_' in column names
#     data_df = data_df.rename(columns=lambda x: x.replace('-', '_'))
    
#     # jsonify (serialize) dict and lst object in some columns
#     for col_name in jsonify_col_lst:
#         data_df[col_name] = data_df[col_name].apply(json.dumps)
    
#     # add data to database one by one to only reject record that would be already present
#     try:
#         data_df.to_sql('birds', con=db, if_exists='append', index=False, chunksize=1000)
#     except sqlite3.IntegrityError as e:
#         print(f"Integrity constraint violation error: {e}")


# """
# Command line options to handle bird database 
# """

# @click.command('init-db')
# # @click.option('--init-db', help='Create empty DB. Will delete any previously existing db')
# def init_db_command():
#     """Clear the existing data and create new tables."""
#     init_db()
#     click.echo('Initialized the database.')


# @click.command('fill-db')
# @click.argument('file_path', default=None)
# # @click.option('--fill-db', default=None, help='add a json file to existing database')
# def fill_db_command(file_path):
#     """Add the content of a json file to the database"""
#     if file_path is None:
#         click.echo('Please provide a json file with the fill-db command')
#     else:
#         error_message = fill_db(file_path=file_path)
#         if error_message is None:
#             click.echo(f'Added {file_path} the database.')
#         else:
#             click.echo(f'{error_message}')


# @click.command('backup-db')
# # @click.option('--backup-db', help='create a backup of the current database')
# def backup_db_command():
#     """Create a db backup"""
#     click.echo('Work in progress. This command does nothing yet.')


# def init_app(app):
#     app.teardown_appcontext(close_db)
#     app.cli.add_command(init_db_command)
#     app.cli.add_command(fill_db_command)
#     app.cli.add_command(backup_db_command)