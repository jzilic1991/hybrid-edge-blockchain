import math
import random
import numpy as np
from abc import ABC, abstractmethod

from util import ResponseTime, Settings, Util, CommDirection
from task import Task


# Template method pattern
class EdgeQueue (ABC):


  # comm_direct is for communication queue direction (downlink or uplink) and site_name is for execution queue
  def __init__ (self, total, arrival_rate = 0.0, task_size_rate = 0.0, comm_direct = None, site_name = None):

    self._total = total
    self._comm_direct = comm_direct
    self._site_name = site_name
    self._arrival_rate = arrival_rate
    self._task_size_rate = task_size_rate
    self._workload = list ()


  def est_lat (cls, task):

    workload = cls._est_arriv ()
    util = cls._est_util (workload)
    
    return cls._est_wait_time (workload, util) + cls._srv_time (task, util)


  def act_lat (cls, task):

    cls._workload.extend (cls._act_arriv (task))
    util = cls._act_util (task)
    cls._print_act_workload ()
    total_lat = cls._act_wait_time (util) + cls._srv_time (task, util)
    cls._workload.clear ()

    return total_lat


  def set_arrival_rate (cls, rate):

    cls._arrival_rate = rate


  def set_task_size_rate (cls, rate):

    cls._task_size_rate = rate


  def _est_util (cls, workload):

    # estimated workload is a numeric scalar
    print ("Estimating utilization - workload: " + str (workload) + ", total: " + str (cls._total))
    print ("Estimated util = " + str (workload / cls._total))
    return workload / cls._total


  def _act_util (cls, task):

    util = 0.0
    
    # actual workload is a list of floats i.e. task sizes
    for w in cls._workload:

      if type (w) == float:
        
        util += w / cls._total
        continue

      util += task.get_mi () / cls._total
    
    return util
  

  def _est_arriv (cls):

    return cls._arrival_rate * cls._task_size_rate


  def _act_arriv (cls, task):

    workload = list ()

    # workload.append (site.gen_workload ())
    numb_of_tasks = cls._gen_num_of_tasks ()

    for i in range (numb_of_tasks):
          
      workload.append (cls._gen_task_size ())

    workload.append (task)
    random.shuffle (workload)

    return workload


  def _print_act_workload (cls):

    queue_type = None
    if cls._comm_direct == CommDirection.UPLINK:

      queue_type = "offloading"

    elif cls._comm_direct == CommDirection.DOWNLINK:

      queue_type = "delivery"

    elif cls._site_name != None:

      queue_type = "execution"

    print ("Task " + str (queue_type) + " queue actual workload: " + str (cls._workload))


  def _gen_task_size (cls):

    return random.expovariate (cls._task_size_rate)


  def _gen_num_of_tasks (cls):

    return np.random.poisson (lam = cls._arrival_rate)


  def _est_wait_time (cls, workload, util):

    pass


  def _act_wait_time (cls, util):

    pass


  def _srv_time (cls, task, util):

    pass




class CommQueue (EdgeQueue):


  def _est_wait_time (cls, workload, util):
    
    print ("CommQueue - Estimating waiting time: workload: " + str (workload) + \
      ", total capacity: " + str (cls._total) + ", utilization: " + str (util))
    print ("CommQueue Total - util = " + str (cls._total - util))
    print ("CommQueue - Estimated waiting time is " + str (workload / (cls._total - util)))
    return workload / (cls._total - util)


  def _act_wait_time (cls, util):

    for i in range (len (cls._workload)):

      if type (cls._workload[i]) == Task:
        
        if i != 0:
          print ("CommQueue Task index in workload list is " + str (i))
          print ("CommQueue Total - util = " + str (cls._total - util))
          print ("CommQueue Workload list until Task is " + str (cls._workload[:(i - 1)]))
          return sum (cls._workload[:(i - 1)]) / (cls._total - util)

        return 0.0

    raise ValueError ("Task should be present in the workload list: " + str (cls._workload))
        

  def _srv_time (cls, task, util):

    avail = cls._total - util
    service_time = task.get_data_in () / (avail * math.log (1 + Settings.SNR, 2))
    print ("CommQueue - Service time: " + str (service_time))
    
    return service_time




class CompQueue (EdgeQueue):


  def _est_wait_time (cls, workload, util):
   
    print ("CompQueue Estimating waiting time: workload = " + str (workload) + ", util = " + str (util) + ", avail = " + str (1 - util))
    print ("CompQueue Estimated waiting time (workload) / (cls._total - util) = " + str (workload / (cls._total - util)))
    return workload / (cls._total - util)


  def _act_wait_time (cls, util):
    
    for i in range (len (cls._workload)):

      if type (cls._workload[i]) == Task:
        
        if i != 0:
          print ("CompQueue Task index in workload list is " + str (i))
          print ("CompQueue Total - util = " + str (cls._total - util))
          print ("CompQueue Workload list until Task is " + str (cls._workload[:(i - 1)]))
          
          return sum (cls._workload[:(i - 1)]) / (cls.._total - util)

        return 0.0

    raise ValueError ("Task was not found in the workload: " + str (cls._workload))


  def _srv_time (cls, task, util):

    print ("CompQueue - Available capacity: " + str (cls._total - util))
    return task.get_mi () / (cls._total - util)      
