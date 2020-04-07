__author__ = "Alec Bailey"
__email__ = "ajbailey3@wisc.edu"

import copy
import csv
from copy import deepcopy
import math
import scipy
import datetime

# Define headers for later use (getting latest date etc)
headers = []


# Load all data from CSV file into a dictionary
#
# Data structure takes the following form:
# A list of dictionaries, one for each row in the dataset, where
# each row represents either a country or a province/state within
# a country (this is maintained for clustering purposes)
def load_data(filepath):
    global headers
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


# Takes in one row from the data loaded from the previous function, calculates the
# corresponding x, y values for that region as specified in the video,
# and returns them in a single structure.
# Where X is is the number of days since the number of cases was 1/10th current
# and Y is the number of days since the number of cases was 1/100th current
def calculate_x_y(time_series: dict):
    global headers
    # Get the latest date from the file headers
    latest_date = headers[len(headers) -1]
    # Access the number of cases at the latest date
    number_of_cases = time_series[latest_date]

    # Calculate the x and y number of cases
    x_cases = math.floor(int(number_of_cases) / 10)
    y_cases = math.floor(int(number_of_cases) / 100)

    # The x and y date which will be returned
    x_date = ''
    y_date = ''

    # Create a copy to not destroy data
    time_series = copy.copy(time_series)
    # Pop off un needed data
    time_series.pop('Province/State')
    time_series.pop('Country/Region')

    # Keep track of the previous date during iteration
    previous_date = ''
    # Iterate over the dict and find the date with the corresponding values
    for key, value in time_series.items():
        print(key, '->', value)
        # When the x value is found, assign it and break from the loop
        if int(value) >= x_cases and x_date == '':
            x_date = previous_date
            break
        # When the y value is found, assign it if it has not yet been assigned
        elif int(value) >= y_cases and y_date == '':
            y_date = previous_date
            previous_date = key
        else:
            previous_date = key

    # Get all dates as datetime format
    x_date = datetime.datetime.strptime(x_date, '%m/%d/%y').date()
    y_date = datetime.datetime.strptime(y_date, '%m/%d/%y').date()
    recent_date = datetime.datetime.strptime(latest_date, '%m/%d/%y').date()

    # Compute the difference between the most recent date cases n and cases = n/10
    x_diff = (recent_date - x_date).days
    # Compute the difference between cases = n/10 and cases = n/100
    y_diff = (x_date - y_date).days

    return x_diff, y_diff


# Preform
def hac(dataset):
    pass

# Defines a main method for running code to prevent import issues
if __name__ == "__main__":


    data = load_data('time_series_covid19_confirmed_global.csv')
    print(data[0])
    print(calculate_x_y(data[0]))