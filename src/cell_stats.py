import numpy as np


class CellStats:

	def __init__(self, cell_name):

		self._id = cell_name
		self._off_dist_samp = dict ()   # of dicts per offloading site key
		self._off_fail_samp = dict ()   # of scalars


	def get_off_dist_samp (cls):

		return cls._off_dist_samp


	def get_off_fail_samp (cls):

		return cls._off_fail_samp


	def get_avg_off_dist (cls):

		result = dict ()

		for key, val in cls._off_dist_samp.items ():

			result[key] = round (sum (val) / len (val), 2)

		rel_result = dict ()
		all_offloads = sum (result.values ())
		for key, val in result.items ():

			rel_result[key] = round (val / all_offloads, 2) * 100

		return ("Offloading distribution (percentage): " + str (rel_result))


	def get_avg_off_fail (cls):

		off_fail = list ()

		for key, _ in cls._off_fail_samp.items ():

			for i in range (len (cls._off_fail_samp[key])):

				if cls._off_dist_samp[key][i] != 0:

					off_fail.append (round (cls._off_fail_samp[key][i] / cls._off_dist_samp[key][i] \
						* 100, 3))

				else:

					off_fail.append (0.0)

		return "Average task failure rate (percentage) is " + \
			str (round (sum (off_fail) / len (off_fail), 3))


	def get_avg_off_fail_dist (cls):

		off_fail = dict ()
		for key, val in cls._off_fail_samp.items ():

			off_fail[key] = round (sum (val) / len (val), 3)

		off_dist = dict ()
		for key, val in cls._off_dist_samp.items ():

			off_dist[key] = round (sum (val) / len (val), 3)

		result = dict ()
		for key in cls._off_fail_samp.keys ():

			if off_dist[key] != 0:

				result[key] = round ((off_fail[key] / off_dist[key]) * 100, 2)

			else:

				result[key] = 0

		return ("Offloading failure distribution (percentage): " + str (result))


	def get_all (cls):

		return cls._id + "\n" + cls.get_avg_off_dist () + '\n' + cls.get_avg_off_fail_dist () +\
			cls.get_avg_off_fail () + '\n'


	def add_off_dist (cls, off_dist_samp):

		for key, val in off_dist_samp.items ():

			if key in cls._off_dist_samp.keys ():

				cls._off_dist_samp[key].append (val)

			else:

				cls._off_dist_samp[key] = [val]


	def add_off_fail (cls, off_fail_samp):

		for key, val in off_fail_samp.items ():

			if key in cls._off_fail_samp.keys ():

				cls._off_fail_samp[key].append (val)

			else:

				cls._off_fail_samp[key] = [val]