import json

from dataset import LoadedData
from util import NodePrototypes




LoadedData.load_dataset ("data/SKYPE.avt")
# LoadedData.print_all_dataset_nodes ()
data = {NodePrototypes.EC: [], NodePrototypes.ED: [], NodePrototypes.ER: [], \
	NodePrototypes.CD: [], NodePrototypes.MD: []}

for d in data:

	nodes = list ()

	if d == NodePrototypes.CD:

		nodes = LoadedData.get_nodes_above_thr (99.0, 11)

	elif d == NodePrototypes.MD:

		nodes = LoadedData.get_nodes_above_thr (100.0, 11)

	else:

		nodes = LoadedData.get_random_dataset_nodes (11)

	for n in nodes:

		data[d].append ({"id": n.get_id (), "avail": n.get_avail (), "ints": n.get_num_of_ints ()})

with open('data/mapping.json', 'w') as outfile:
	
	json.dump(data, outfile, indent = 4)