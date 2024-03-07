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
    
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(data)
    return data, kmeans.labels_


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
data, labels = cluster_cells (parsed_data, num_clusters=30)
plot_topology (data, labels)