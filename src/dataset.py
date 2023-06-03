import re




class LoadedData (object):

	_dataset = None
	_dataset_nodes = None

	@classmethod
	def load_dataset (cls, file):

		cls._dataset = Dataset (file)
		cls._dataset_nodes = list ()

		for n_id, intervals in cls._dataset.get_dataset().items():

			cls._dataset_nodes.append (DatasetNode (n_id, intervals))


	@classmethod
	def get_dataset_node (cls, n_id):

		for node in cls._dataset_nodes:

			if node.get_id () == n_id:

				return node

		return None


	@classmethod
	def get_ids (cls):

		ids = list ()

		for node in cls._dataset_nodes:

			ids.append (node.get_id ())

		return ids


	@classmethod
	def print_all_dataset_nodes (cls):

		for node in cls._dataset_nodes:

			node.print_dataset_info ()




class DatasetNode:

	def __init__ (self, n_id, intervals):
		
		self._id = n_id
		self._intervals = intervals
		self._avail = self.__compute_avail ()

		# self.print_dataset_info ()


	def get_id (cls):

		return cls._id


	def get_avail (cls):

		return cls._avail


	def get_intervals (cls):

		return cls._intervals


	def print_dataset_info (cls):

		print ("ID:" + cls._id + ", avail: " + str (cls._avail) + "%, intervals: " + \
			str (len(cls._intervals)))
		# print (cls._intervals)


	def is_avail_or_not (cls, t):

		for interval in cls._intervals:

			if (interval[0] < t) and (interval[1] > t):

				return True

			elif (interval[0] > t) and (interval[1] > t):

				break

		return False


	def __compute_avail (cls):

		avail = 0.0

		for inter in cls._intervals:

			avail += inter[1] - inter[0]

		return round (avail * 100, 2)




class Dataset:

	def __init__ (self, file):

		self._storage = self.__init_storage (file)


	def get_dataset (cls):

		return cls._storage


	def __init_storage (cls, file):

		storage = dict ()
		file = open (file, "r")

		for line in file.readlines ():

			line = line.split (" ")

			for i in range(len(line)):

				line[i] = cls.__data_cleaning (line[i])

			tmp = cls.__min_max_normalization (line[1:])
			storage[line[0]] = cls.__create_normal_avail_data (tmp)

		return storage


	def __data_cleaning (cls, line):

		line = re.sub ("\t\d*", "", line)
		line = re.sub ("\n", "", line)

		return line


	def __min_max_normalization (cls, tmp):

		max_e = int (tmp[len(tmp) - 1])
		min_e = int (tmp[0])

		for i in range(len (tmp)):

			tmp[i] = round ((int (tmp[i]) - min_e) / (max_e - min_e), 4)

		return tmp


	def __create_normal_avail_data (cls, tmp):

		tmp_list = list ()

		for i in range (0, len (tmp), 2):

			tmp_list.append((tmp[i], tmp[i + 1]))

		return tmp_list


# LoadedData.load_dataset ("data/SKYPE.avt")
# LoadedData.print_all_dataset_nodes ()
# createDatasetNodes("data/SKYPE.avt")
# createDatasetNodes("data/PlanetLAB.avt")
# createDatasetNodes("data/LDNS.txt")