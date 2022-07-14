import csv
import time
from datetime import datetime

headers = ('temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6',
         'temp_7', 'space', 'temp_8', 'temp_9', 'temp_10', 'temp_11', 
         'temp_12',"Heat_flux_1", "Heat_flux_2","Power_input","conductivity", "tiempo")


def persist_data(data: dict, path: str):
 
    with open(path, 'a+') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writerow(data)

def create_file(path: str):

    with open(path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()

def init_file(directory: str):
    # creating the file name.
    date_time = datetime.fromtimestamp(time.time())
    date_time = str(date_time).replace(':', '-').split('.')[0]
    file = f'{directory}/{date_time}.csv'

    create_file(file)
    return file

def write_data(time_date, data, Heat_flux_1,Heat_flux_2, power,con,file):
    dict_data ={}
    dict_data['tiempo'] = time_date.strftime("%Y-%m-%d %H:%M:%S")
    dict_data['space'] = " "
    dict_data['Heat_flux_1'] = Heat_flux_1
    dict_data['Heat_flux_2'] = Heat_flux_2
    dict_data['Power_input'] = power
    dict_data['conductivity'] = con
    for i, dat in enumerate(data,1):
        dict_data[f"temp_{i}"] = dat
    persist_data(dict_data, file)