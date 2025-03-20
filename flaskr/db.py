import pathlib
import csv
import random

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

    return pd.DataFrame(sample, columns=header)


def load_bird_names(filepath: pathlib.Path) -> list[str]:
    # return all bird names (english names) as a list
    bird_names = []
    name_index = None
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        header = next(reader)  # Read header
        
        for i, col_name in enumerate(header):
            print(col_name)
            if col_name == 'en':
                name_index = i
        if name_index is not None:
            for _, row in enumerate(reader, start=1):
                bird_names.append(row[name_index])
    
    return bird_names


def get_bird_data(filepath: pathlib.Path, bird_names: list[str]) -> pd.DataFrame:
    # returns a dataframe with all data from a list of bird names
    
    # avoid loading all the file at once
    kept_rows = []
    name_index = None
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        header = next(reader)  # Read header
        
        for i, col_name in enumerate(header):
            print(col_name)
            if col_name == 'en':
                name_index = i
        if name_index is not None:
            for _, row in enumerate(reader, start=1):
                if row[name_index].strip().lower() in bird_names:
                    kept_rows.append(row)
    
    return pd.DataFrame(kept_rows, columns=header) 
