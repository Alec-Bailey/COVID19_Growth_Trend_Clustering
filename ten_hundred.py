__author__ = "Alec Bailey"
__email__ = "ajbailey3@wisc.edu"

import copy
import csv
from copy import deepcopy
import math
import scipy.cluster
import scipy.spatial.distance
import numpy
import datetime
from collections import OrderedDict

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
        data = OrderedDict({'Province/State': None, 'Country/Region': None})
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
    latest_date = headers[len(headers) - 1]
    # Access the number of cases at the latest date
    number_of_cases = int(time_series[latest_date])

    # If there are no cases, return none and exclude the value
    if int(number_of_cases) == 0:
        return math.nan, math.nan

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

    # Iterate over the dict and find the date with the corresponding values
    for key, value in time_series.items().__reversed__():
        # When x value is found, assign it
        if int(value) <= x_cases and x_date == '':
            x_date = key
        # When the y value is found, assign it and break from the loop
        if int(value) <= y_cases and y_date == '':
            y_date = key
            break

    # Get all dates as datetime format
    x_date = datetime.datetime.strptime(x_date, '%m/%d/%y').date()
    recent_date = datetime.datetime.strptime(latest_date, '%m/%d/%y').date()

    # Compute the difference between the most recent date cases n and cases = n/10
    x_diff = (recent_date - x_date).days

    # Filter out data where a n/100 y_date cannot be found
    # for example Beijing
    if y_date == '':
        return x_diff, math.nan

    y_date = datetime.datetime.strptime(y_date, '%m/%d/%y').date()
        # Compute the difference between cases = n/10 and cases = n/100
    y_diff = (x_date - y_date).days

    return x_diff, y_diff


# Preform HAC with single-linkage
def hac(dataset):

    # Filter out the nan data points and append valid data to the working list
    vectors = []
    for x_y in dataset:
        if not math.isnan(x_y[0]) and not math.isnan(x_y[1]):
            vectors.append(x_y)

    # Maintains a list of 'working vectors' which can be removed from in order to
    # keep track of which vectors are still not merged
    working_vectors = copy.deepcopy(vectors)

    # Defines m, which is the initial number of data points,creating m-1 clusters
    m = len(vectors)

    # Create a matrix of m-1 rows and 4 columns where m is the number of data entries
    # which intuitively has a minimum of m-1 clusters, and 4 columns
    # with the form (cluster 1, cluster 2, distance between clusters, number of data points in cluster)
    working_clusters = []
    for i in range(0, len(vectors)):
        # [Cluster 1, Cluster2, Distance, Data Points, Cluster Index]
        working_clusters.append([i, i, 0, 1, [vectors[i]]])

    # Define the array of clusters which will be added to
    clusters = []

    for x in range(0, len(working_clusters) -1):
        # Create the first cluster traversing backwards so that the lowest index cluster
        # takes precedence in a tie
        best = [float('inf'), []]
        for i in range(0, len(working_clusters)):
            for j in range(i, len(working_clusters)):
                # Do not compare a cluster to itself
                if i != j:
                    # Get the smallest euclidean distance between points, when comparing a cluster
                    # use the two closest points

                    # Create two lists of points which are recursively found
                    pointsA = working_clusters[j][4]
                    pointsB = working_clusters[i][4]

                    min_dist = float('inf')
                    # compare all returned points and find the minimum distance
                    for pA in pointsA:
                        for pB in pointsB:
                            distance = scipy.spatial.distance.euclidean(pA, pB)
                            if distance < min_dist:
                                min_dist = distance

                    # If this is better than the previous best, set it
                    if min_dist < best[0]:
                        best = [min_dist, [working_clusters[i], working_clusters[j]]]

        # Add the first cluster to the list of clusters
        clusters.append([best[1][0][0], best[1][1][0], best[0], best[1][0][3] + best[1][1][3]])
        # Change the first indexed working cluster to the created cluster
        working_clusters.append([m + x, m + x, best[0], best[1][0][3] + best[1][1][3], best[1][0][4] + best[1][1][4]])
        # Pop off the merged cluster from working clusters
        working_clusters.remove(best[1][0])
        working_clusters.remove(best[1][1])

    return numpy.asarray(clusters)


# Defines a main method for running code to prevent import issues
if __name__ == "__main__":

    data = load_data('time_series_covid19_confirmed_global.csv')

    observation_vectors = []
    for point in data:
        x_y = calculate_x_y(point)
        observation_vectors.append(x_y)

    # print(observation_vectors)
    hac = hac(observation_vectors)

    print(hac)