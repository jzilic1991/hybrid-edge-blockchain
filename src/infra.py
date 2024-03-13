from util import Settings

import numpy as np
import csv
from sklearn.cluster import KMeans


class Infrastructure:

  _clustered_nodes = tuple ()


  @ classmethod
  def init_infra (cls, file_path, num_clusters, topology_dict, off_site_dict):

    parsed_data = cls.__parse_topology_file (file_path)
    cluster_labels = cls.__clustering_cells (parsed_data, num_clusters)
    cls._clustered_nodes = cls.__create_cluster_nodes (cluster_labels, topology_dict, off_site_dict)
  
  
  @classmethod
  def __parse_topology_file (cls, file_path):
    
    data = dict ()
    
    with open(file_path, 'r') as file:
        
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            
            key = row[3] # cell ID (land area code)
            data[key] = { "latitude": float (row[7]), "longitude": float (row[6]) }
    
    return data


  @classmethod
  def __clustering_cells(cls, parsed_data, num_clusters):

    data = tuple ()
    
    for values in parsed_data.values ():
        
        latitude = float (values["latitude"])
        longitude = float (values["longitude"])
        data += ((latitude, longitude), )
    
    np.random.seed (42)
    kmeans = KMeans (n_init = 10, n_clusters = num_clusters)
    kmeans.fit (data)
    
    return kmeans.labels_


  @classmethod
  def __create_cluster_nodes (cls, labels, topology_dict, off_site_dict):

    cluster_nodes = dict ()
    cluster_node_cnt = dict ()
    node_prototypes = [NodePrototypes.ER, NodePrototypes.ED, NodePrototypes.EC, NodePrototypes.CD]

    for i in range (len (labels)):

        if not labels[i] in cluster_nodes:
            
            cluster_node_cnt[labels[i]] = 0
        
        cluster_node_cnt[labels[i]] += 1

    for label in cluster_node:

      category_sizes = cls.__label_node_types (cluster_node_cnt[label])

      for size in category_sizes:

        for i in range (size):

          if not label in cluster_nodes:

            cluster_nodes = list ()
          
          cluster_nodes[labels[i]].append (OffloadingSite (off_site_dict, topology_dict))

    return cluster_nodes


  @classmethod
  def __label_node_types (cls, num_items, num_categories = 4):
    
    # Initialize an empty list to store the sizes of each category
    category_sizes = [0] * num_categories
    
    # Calculate the base size of each category
    base_size = num_items // num_categories
    
    # Calculate the number of categories that will have one more item
    num_categories_with_extra_item = num_items % num_categories
    
    # Distribute the items into categories
    for i in range(num_items):
        # Find the category index to place the current item
        category_index = i % num_categories
        
        # Increment the size of the category
        category_sizes[category_index] += 1
        
        # Check if the current category already has an extra item
        if category_index < num_categories_with_extra_item:
            # If so, increment the base size of this category
            category_sizes[category_index] += 1
    
    return category_sizes
