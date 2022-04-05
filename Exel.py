import csv

headers = ('temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6', 'temp_7', 'space', 'temp_8', 'temp_9', 'temp_10', 'temp_11', 'temp_12', "tiempo")


def persist_data(data: dict, path: str):
 
    with open(path, 'a+') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writerow(data)

def create_file(path: str):

    with open(path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()
