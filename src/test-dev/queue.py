import random
import math
import numpy as np


SNR = 5


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


class EdgeQueue:

	def __init__ (self, total):

		self._total = total
		self._util = 0.0
		self._workload = 0.0
		self._latency = 0.0


	def arrival (cls, mds):

		cls._workload = 0.0

		# compute complete workload of all mobile devices
		for md in mds:

			cls._workload += md.get_workload ()

		# compute utilization factor
		cls.__est_util (mds)

	
	def get_utilization (cls):

		return cls._util

	
	def est_latency (cls, task_workload):

		# waiting time is depended on current overall workload while service time depends on target offloaded task
		return cls.__est_wait_time () + cls.__est_srv_time (task_workload)


	def __est_util (cls, mds):

		util = 0.0

		for md in mds:

			util += md.get_workload () / cls._total

		cls._util = util
	

	def __est_wait_time (cls):

		return cls._workload / (cls._total - cls._util)
	

	def __est_srv_time (cls, task_workload):

		avail = cls._total - cls._util
		
		return task_workload / (avail * math.log (1 + SNR, 2))


mobile_net = list ()
comm_queue = EdgeQueue (1000)

for i in range (30):

	mobile_net.append (MobileDevice (2, 3))

for md in mobile_net:
	
	print (str (md) + " workload size: " + str (md.gen_workload ()))

md = MobileDevice (2, 3)
print ("Estimated offloading latency: " + str (comm_queue.est_latency (md.gen_workload ())))
