import re

class Dataset:

	def __init__ (self, file):

		self._storage = self.__init_storage (file)

		print (self._storage)


	def __init_storage (cls, file):

		storage = dict ()
		file = open (file, "r")

		for line in file.readlines ():

			line = line.split (" ")

			for i in range(len(line)):

				line[i] = re.sub ("\t\d*", "", line[i])
				line[i] = re.sub ("\n", "", line[i])

			tmp = line[1:]

			max_e = int (tmp[len(tmp) - 1])
			min_e = int (tmp[0])

			for i in range(len (tmp)):

				tmp[i] = (int (tmp[i]) - min_e) / (max_e - min_e)

			tmp_list = list ()
			for i in range (0, len (tmp), 2):

				tmp_list.append((tmp[i], tmp[i + 1]))

			storage[line[0]] = tmp_list

		return storage


Dataset ("data/SKYPE.avt")