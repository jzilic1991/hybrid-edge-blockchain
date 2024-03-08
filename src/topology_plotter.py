import matplotlib.pyplot as plt
from topology_generator import parse_topology_file, cluster_cells


def plot_topology (data, labels):

    lats = list ()
    longs = list ()
    
    for gps_coord in parsed_data.values ():

        lats.append (gps_coord ["latitude"])
        longs.append (gps_coord ["longitude"])

    plt.figure(figsize = (10, 6))
    plt.scatter(longs, lats, c=labels, cmap='viridis', alpha=0.5)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Clustered Cells')
    plt.grid(True)
    plt.show()


parsed_data = parse_topology_file ('data/232.csv')
data, labels = cluster_cells (parsed_data, num_clusters = 30)
# plot_topology (data, labels)
print ("Labels: " + str (labels))
# print ("Data: " + str (data))
