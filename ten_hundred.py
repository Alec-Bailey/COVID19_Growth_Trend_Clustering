__author__ = "Alec Bailey"
__email__ = "ajbailey3@wisc.edu"

import csv
from copy import deepcopy
import math


# Load all data from CSV file into a dictionary
#
# Data structure takes the following form:
# A list of dictionaries, one for each row in the dataset, where
# each row represents either a country or a province/state within
# a country (this is maintained for clustering purposes)
def load_data(filepath):
    # Define a list of all data columns
    all_data_columns = []

    # Create CSV Reader
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)

        # Get the list of headers (Keys) for data
        headers = list(next(reader))

        # Initialize a data array containing all data
        # to None for every entry
        data = {'Province/State': None, 'Country/Region': None}
        # Include the first 2 columns to ignore lat/long data
        for i in range(4, len(headers)):
            data[headers[i]] = None

        # Iterate over every line in the data and append all dictionaries to full list
        for line in reader:
            # Add all data to data dictionary for entry
            data_entry = deepcopy(data)
            for i in range(0, 2):
                data_entry[headers[i]] = line[i]
            for i in range(4, len(headers)):
                data_entry[headers[i]] = line[i]
            all_data_columns.append(data_entry)

        csvfile.close()

    return all_data_columns


data = load_data('time_series_covid19_confirmed_global.csv')

print(data[0])
