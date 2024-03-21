import json

from dataset import LoadedData
from util import NodePrototypes


LoadedData.load_dataset ("data/SKYPE.avt")
# LoadedData.print_all_dataset_nodes ()
data = {NodePrototypes.EC: [], NodePrototypes.ED: [], NodePrototypes.ER: [], \
  NodePrototypes.CD: [], NodePrototypes.MD: []}
NODE_COUNT = 50

for d in data:

  nodes = list ()

  if d == NodePrototypes.CD:

    nodes = LoadedData.get_nodes_above_thr (0.99, NODE_COUNT)

  elif d == NodePrototypes.MD:

    nodes = LoadedData.get_nodes_above_thr (1.0, NODE_COUNT)

  else:

    nodes = LoadedData.get_random_dataset_nodes (NODE_COUNT)

  for n in nodes:

    data[d].append ({"id": n.get_id (), "avail": n.get_avail (), "ints": n.get_num_of_ints ()})


with open('data/mapping.json', 'w') as outfile:

  json.dump(data, outfile, indent = 4)
