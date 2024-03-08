import numpy as np
import csv
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def parse_topology_file (file_path):
    
    data = dict ()
    
    with open(file_path, 'r') as file:
        
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            
            key = row[3]
            data[key] = { "latitude": float (row[7]), "longitude": float (row[6]) }

            # data.append ({
            #     'longitude': float(row[6]),
            #     'latitude': float(row[7]),
            # })
    
    return data


def cluster_cells(parsed_data, num_clusters=3):

    data = list ()
    
    for values in parsed_data.values ():
        
        latitude = float(values["latitude"])
        longitude = float(values["longitude"])
        data.append([latitude, longitude])    
    
    np.random.seed(42)
    kmeans = KMeans(n_init = 10, n_clusters = num_clusters)
    kmeans.fit(data)
    return data, kmeans.labels_
