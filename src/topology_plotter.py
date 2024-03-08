import matplotlib.pyplot as plt
import networkx as nx
from topology_generator import *


def plot_topology (data, labels):

    lats = list ()
    longs = list ()
    
    for gps_coord in data:

        lats.append (gps_coord [0])
        longs.append (gps_coord [1])

    plt.figure(figsize = (10, 6))
    plt.scatter(longs, lats, c = labels, cmap = 'viridis', alpha = 0.5)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Clustered Cells')
    plt.grid(True)
    plt.show()


def plot_graph (graph):

    nx.draw(graph, with_labels = False, node_color = 'skyblue', node_size = 1000, font_size = 12, font_weight = 'bold')
    plt.show()


parsed_data = parse_topology_file ('data/232.csv')
data, labels = cluster_cells (parsed_data, num_clusters = 30)
cluster_nodes = create_cluster_nodes (data, labels)
graph = create_graph (cluster_nodes)
plot_topology (data, labels)
# plot_graph (graph)
# print ("Labels: " + str (labels))
# print ("Data: " + str (data))