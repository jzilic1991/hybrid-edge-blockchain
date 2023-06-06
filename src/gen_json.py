import json

from dataset import LoadedData




LoadedData.load_dataset ("data/SKYPE.avt")
# LoadedData.print_all_dataset_nodes ()
data = {"EC": [], "ED": [], "ER": [], "CD": []}

for d in data:

	nodes = LoadedData.get_random_dataset_nodes (10)

	for n in nodes:

		data[d].append ({"id": n.get_id (), "avail": n.get_avail (), "ints": n.get_num_of_ints ()})

with open('data/mapping.json', 'w') as outfile:
	
	json.dump(data, outfile, indent = 4)