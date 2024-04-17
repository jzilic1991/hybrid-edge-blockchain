import matplotlib.pyplot as plt
from infra import Infrastructure

import json


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


Infrastructure.get_clustered_cells ("data/AT-Cell.csv", \
    json.load (open ("data/off-sites.json")))
(data, labels) = Infrastructure.get_plotting_data ()
print (len (data))
print (len (labels))
plot_topology (data, labels)