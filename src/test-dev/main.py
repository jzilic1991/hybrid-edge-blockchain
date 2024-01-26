import random
import math
import numpy as np

from md import MobileDevice
from edge_queue import EdgeQueue


mobile_net = list ()
comm_queue = EdgeQueue (1000)

for i in range (30):

	mobile_net.append (MobileDevice (2, 3))

for md in mobile_net:
	
	print (str (md) + " workload size: " + str (md.gen_workload ()))

md = MobileDevice (2, 3)
print ("Estimated offloading latency: " + str (comm_queue.est_latency (md.gen_workload ())))
