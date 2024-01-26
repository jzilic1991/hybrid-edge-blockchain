import numpy as np
import random


class MobileDevice:

	def __init__ (self, pois_rate, exp_rate):

		self._pois_rate = pois_rate
		self._exp_rate = exp_rate

	
	def gen_workload (cls):

		return cls.__gen_task_size () * cls.__gen_numb_of_tasks ()
	

	def __gen_task_size (cls):

		return random.expovariate (cls._exp_rate)

	
	def __gen_numb_of_tasks (cls):

		return np.random.poisson (lam = cls._pois_rate, size = 1)
