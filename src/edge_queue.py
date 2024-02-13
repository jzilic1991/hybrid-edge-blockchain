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

    workload = list ()

    for ele in cls._workload:

      workload.append (ele)

    workload.extend (cls._arrival (task))
    util = cls._utilization_factor (workload, task)
    
    return cls._waiting_time (workload, util) + cls._service_time (task, util)


  def act_lat (cls, task):

    cls._workload.extend (cls._arrival (task))
    util = cls._utilization_factor (cls._workload, task)
    cls._print_workload (cls._workload)
    total_lat = cls._waiting_time (cls._workload, util) + cls._service_time (task, util)
    cls._workload = cls._residual_workload (cls._workload)

    return total_lat


  def set_arrival_rate (cls):

    cls._arrival_rate = np.random.poisson (lam = cls._arrival_rate)


  def set_task_size_rate (cls):

    cls._task_size_rate = random.expovariate (cls._task_size_rate)

  
  def _arrival (cls, task):

    workload = list ()

    # workload.append (site.gen_workload ())
    numb_of_tasks = cls._gen_num_of_tasks ()

    for i in range (numb_of_tasks):
          
      workload.append (cls._gen_task_size ())

    workload.append (task)
    random.shuffle (workload)

    return workload


  def _utilization_factor (cls, workload, task):

    util = 0.0
    
    # actual workload is a list of floats i.e. task sizes
    for w in workload:

      if type (w) == float:
        
        util += w / cls._total
        continue

      util += task.get_mi () / cls._total
    
    return util


  def _print_workload (cls, workload):

    queue_type = None
    
    if cls._comm_direct == CommDirection.UPLINK:

      queue_type = "offloading"

    elif cls._comm_direct == CommDirection.DOWNLINK:

      queue_type = "delivery"

    elif cls._site_name != None:

      queue_type = "execution"

    # here is the code for converting task class object into floating point task size 
    conv_workload = list ()
    for ele in workload:
        
      if type (ele) == float:
        
        conv_workload.append (ele)
        continue

      conv_workload.append (ele.get_mi ())

    print ("Task " + str (queue_type) + " queue has an actual sum of workload: " + str (sum (conv_workload)) + ", workload: " + str (conv_workload))

  
  def _residual_workload (cls, workload):

    k = None

    for i in range (len (workload)):

      if type (workload[i]) == Task:

        k = i
        break

    workload = workload[(k + 1):]

    return workload


  def _gen_task_size (cls):

    return random.expovariate (cls._task_size_rate)


  def _gen_num_of_tasks (cls):

    return np.random.poisson (lam = cls._arrival_rate)


  def _waiting_time (cls, workload, util):

    pass


  def _service_time (cls, task, util):

    pass




class CommQueue (EdgeQueue):


  def _waiting_time (cls, workload, util):

    for i in range (len (workload)):

      if type (workload[i]) == Task:
        
        if i != 0:
          
          # print ("CommQueue workload until task: " + str (workload[:i]) + ", sum(workload) = " + str (sum (workload[:i])) + ", total: " + str (cls._total) + ", util: " + str (util) + ", ACTUAL WAITING TIME: " + str (sum (workload[:i]) / (cls._total - util)))
          return sum (workload[:i]) / (cls._total - util)

        return 0.0

    raise ValueError ("Task should be present in the workload list: " + str (workload))
        

  def _service_time (cls, task, util):

    avail = cls._total - util
    
    return task.get_data_in () / (avail * math.log (1 + Settings.SNR, 2))




class CompQueue (EdgeQueue):


  def _waiting_time (cls, workload, util):
    
    for i in range (len (workload)):

      if type (workload[i]) == Task:
        
        if i != 0:
          
          # print ("CompQueue workload until task: " + str (workload[:i]) + ", sum(workload) = " + str (sum (workload[:i])) + ", total: " + str (cls._total) + ", util: " + str (util) + ", ACTUAL WAITING TIME: " + str (sum (workload[:i]) / (cls._total - util)))
          return sum (workload[:i]) / (cls._total - util)

        return 0.0

    raise ValueError ("Task was not found in the workload: " + str (workload))


  def _service_time (cls, task, util):

    return task.get_mi () / (cls._total - util)      
