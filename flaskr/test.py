# -*- coding: utf-8 -*-
"""
test file
"""
from db import load_random_rows_from_csv, load_bird_names
import random
import os
import pathlib

test_path = pathlib.Path(os.path.dirname(__file__)) / 'tests' / 'test_data' / 'test_bird_data.csv'
random.seed(0)
selected_rows = load_random_rows_from_csv(test_path, nb_rows=1)
selected_birds = load_bird_names(test_path)
print(selected_rows['id'].values[0])
print(selected_birds)




