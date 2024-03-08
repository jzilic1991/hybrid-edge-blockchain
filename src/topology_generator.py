import numpy as np
import csv
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import KMeans


def parse_topology_file (file_path):
    
    data = dict ()
    
    with open(file_path, 'r') as file:
        
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            
            key = row[3]
            data[key] = { "latitude": float (row[7]), "longitude": float (row[6]) }
    
    return data


def cluster_cells(parsed_data, num_clusters = 3):

    data = tuple ()
    
    for values in parsed_data.values ():
        
        latitude = float (values["latitude"])
        longitude = float (values["longitude"])
        data += ((latitude, longitude), )
    
    np.random.seed (42)
    kmeans = KMeans (n_init = 10, n_clusters = num_clusters)
    kmeans.fit (data)
    
    return data, kmeans.labels_


def create_cluster_nodes (data, labels):

    cluster_nodes = dict ()

    for i in range (len (labels)):

        if not labels[i] in cluster_nodes:
            
            cluster_nodes[labels[i]] = tuple ()
        
        cluster_nodes[labels[i]] += (data[i], )

    return cluster_nodes


def create_graph (cluster_nodes):

    # Create a new graph
    G = nx.Graph()
    
    for label in cluster_nodes:

        G.add_nodes_from (cluster_nodes[label])
        G.add_edges_from (nx.complete_graph (cluster_nodes[label]).edges ())

    # Access and manipulate the graph as needed
    # print ("Number of graph nodes: " + str (G.number_of_nodes ()))
    # print ("Number of graph edges: " + str (G.number_of_edges ()))

    return G