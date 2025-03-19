# Execute this file to build the french bird dataset file
import requests
import csv
import time
from itertools import chain
import pathlib

def get_french_bird_songs() -> list[dict]:
    base_url = "https://www.xeno-canto.org/api/2/recordings"
    page = 1
    species_set = set()
    end_not_reached = 1
    kept_records = []

    # Only keep part of the data to avoid saving too much
    keys_to_keep = [
        'id',
        'gen',
        'sp',
        'en',
        'lat',
        'lng',
        'url',
        'file',
        'file-name'
    ]

    # API only return a single apge each time. Need to loop over pages
    while end_not_reached:
        # Select French birds songs with the highest quality
        params = {"query": ["cnt:France", "q:A", "type:song"], "page": page}
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code} at page {page}")
            return kept_records  # failsafe to retrieve at least some record if something fails

        data = response.json()
        print(f"extracting page {page} over {data['numPages']}")
        
        # Extract unique species names
        for record in data["recordings"]:
            species_name = f"{record['gen']} {record['sp']}"
            # only consider species whose song can be downloaded and have a vernacular name (some are not available for conservation purpose)
            if species_name not in species_set and record['file'] != '' and record['en'] != '':
                filtered_data = {key: record[key] for key in keys_to_keep}
                species_set.add(species_name)
                kept_records.append(filtered_data.copy()) # only keep the first record found for each species

        # Iterate over pages
        if page >= int(data["numPages"]):
            end_not_reached = 0  # Stop when reached the last page
        page += 1
        time.sleep(3)  # avoid overloading the api
    
    return kept_records


def save_records(record_lst: list[dict], filename: pathlib.Path) -> None:
    headers = record_lst[0].keys()  # all records have the same keys
    
    with open(filename, mode="w", newline="", encoding="utf-8", ) as file:
        writer = csv.DictWriter(file, fieldnames=headers, delimiter="|")
        writer.writeheader()  # Write headers
        writer.writerows(record_lst)  # Write data
    
    print(f"Data saved to {filename}")


if __name__ == '__main__':
    file_path = pathlib.Path('french_bird_data.csv')
    records = get_french_bird_songs()
    save_records(records, file_path)
