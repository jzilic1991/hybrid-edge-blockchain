from util import Settings, NodePrototypes
from off_site import OffloadingSite

import numpy as np
import csv
from sklearn.cluster import KMeans


class Infrastructure:

  _clustered_nodes = tuple ()
  _data = dict ()
  _cluster_labels = np.array ([])


  @classmethod
  def get_clustered_cells (cls, file_path, off_site_dict, profile = "default", num_clusters = 100):
    _parsed_data = cls.__parse_topology_file (file_path)
    cls._data, cls._cluster_labels = cls.__clustering_cells (_parsed_data, num_clusters)
    cls._clustered_nodes = cls.__create_cluster_nodes (cls._cluster_labels, off_site_dict, profile)

    return cls._clustered_nodes

  @classmethod
  def get_plotting_data (cls):
    return (cls._data, cls._cluster_labels)
  
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
   
    # remove duplicates
    tmp = set (data)
    data_wo_duplicates = tuple (tmp)
    
    # seeding to ensure same clustering
    np.random.seed (42)
    kmeans = KMeans (n_init = 10, n_clusters = num_clusters)
    kmeans.fit (data_wo_duplicates)
    
    return (data_wo_duplicates, kmeans.labels_)


  @classmethod
  def __create_cluster_nodes (cls, labels, off_site_dict, profile):
    cluster_node_cnt = dict ()
    node_prototypes = [NodePrototypes.ER, NodePrototypes.ED, NodePrototypes.EC]

    for i in range (len (labels)):
        if not labels[i] in cluster_node_cnt:            
            cluster_node_cnt[labels[i]] = 1
        
        cluster_node_cnt[labels[i]] += 1

    cluster_nodes = cls.__label_cluster_nodes (cluster_node_cnt, node_prototypes, off_site_dict, profile)
    
    return cluster_nodes

 
  @classmethod
  def __label_cluster_nodes (cls, cluster_node_cnt, node_prototypes, off_site_dict, profile):
    cluster_nodes = dict ()

    for label in cluster_node_cnt:      
      category_sizes = cls.__determine_node_prototype_sizes (cluster_node_cnt[label], len (node_prototypes))

      for i in range (len (category_sizes)):
        for j in range (category_sizes[i]):
          if not label in cluster_nodes:
            cluster_nodes[label] = list ()
          
          cluster_nodes[label].append (OffloadingSite (node_prototypes[i], off_site_dict['off-sites'][node_prototypes[i]], profile = profile))

      cluster_nodes[label].append (OffloadingSite (NodePrototypes.CD, off_site_dict['off-sites'][NodePrototypes.CD], profile = profile))
      cluster_nodes[label].append (OffloadingSite (NodePrototypes.MD, off_site_dict['off-sites'][NodePrototypes.MD], profile = profile))

    return cluster_nodes

  
  @classmethod
  def __determine_node_prototype_sizes (cls, num_items, num_categories):
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

      return category_sizes
