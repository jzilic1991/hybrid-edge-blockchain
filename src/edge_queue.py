import math
import random
import numpy as np
from abc import ABC, abstractmethod

from util import ResponseTime, Settings, Util, CommDirection, ExpRate, PoissonRate
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

    workload.extend (cls._arrival (task = task))
    util = cls._utilization_factor (workload, task = task)
    
    return cls._waiting_time (workload, util) + cls._service_time (task, util)


  def act_lat (cls, task):

    generated_workload = cls._arrival (task = task)
    # print ("Generated workload (arrival rate: " + str (cls._arrival_rate) + \
    #  ", task size rate: " + str (cls._task_size_rate) + "): " + \
    #  str (generated_workload))
    cls._workload.extend (generated_workload)
    util = cls._utilization_factor (cls._workload, task = task)
    cls._print_workload (cls._workload, util)
    total_lat = cls._waiting_time (cls._workload, util) + cls._service_time (task, util)
    cls._workload = cls._residual_workload (cls._workload)

    return total_lat


  def workload_update (cls, time_passed):

    # print ("--- Before update " + cls._site_name + " ---")
    cls._workload.extend (cls._arrival ())
    util = cls._utilization_factor (cls._workload)
    # cls._print_workload (cls._workload, util)
    # print ("--- After update " + cls._site_name + " ---")
    cls._workload = cls._residual_workload (cls._workload, time_passed = time_passed)
    util = cls._utilization_factor (cls._workload)
    cls._print_workload (cls._workload, util)


  def enough_resources (cls, task):

    return cls._utilization_factor (workload, task = task) < 1


  def update_arrival_rate (cls):

    cls._arrival_rate = random.randint (PoissonRate.MIN_RATE, PoissonRate.MAX_RATE)


  def update_task_size_rate (cls):

    cls._task_size_rate = random.uniform (ExpRate.MIN_RATE, ExpRate.MAX_RATE)

  
  def _arrival (cls, task = None):

    workload = list ()

    # workload.append (site.gen_workload ())
    numb_of_tasks = cls._gen_num_of_tasks ()

    for i in range (numb_of_tasks):
          
      workload.append (cls._gen_task_size ())

    if task != None:
        
       workload.append (task)
    
    random.shuffle (workload)

    return workload


  def _utilization_factor (cls, workload, task = None):

    util = 0.0
    
    # actual workload is a list of floats i.e. task sizes
    for w in workload:

      if type (w) == float:
        
        util += w / cls._total
        continue

      if task != None:
        
        util += task.get_mi () / cls._total
    
    return util


  def _print_workload (cls, workload, util):

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
    
    print ("Task " + str (queue_type) + " queue has a util = " + \
      str (round (util * 100, 3)) + " %") #+ ", workload: " + str (conv_workload))
      #str (round (sum (conv_workload), 3)) + " / " + str (cls._total) + " = " + \

  
  def _residual_workload (cls, workload, time_passed = None):

    k = None

    for i in range (len (workload)):

      if type (workload[i]) == Task:

        k = i
        break

    # if task is not found, it means the site which owns this queue has to update its 
    # queue state to remove those tasks that are executed within time passed
    # the case applies to sites which did not receive task class object
    if k == None:

      workload = cls._elapsed_workload (workload, time_passed, cls._utilization_factor (workload)) 
       
    else:
      
      workload = workload[(k + 1):]

    return workload


  def _gen_task_size (cls):

    return random.expovariate (cls._task_size_rate)


  def _gen_num_of_tasks (cls):

    return np.random.poisson (lam = cls._arrival_rate)

  
  def _elapsed_workload (cls, workload, time_passed, util):
    
    pass


  def _waiting_time (cls, workload, util):

    pass


  def _service_time (cls, task, util):

    pass



class CommQueue (EdgeQueue):


  def _elapsed_workload (cls, workload, time_passed, util):

    elapsed_time_accumulated = 0.0
    new_update_task_size = 0.0
    avail = cls._total - util

    # print ("Time passed: " + str (time_passed))

    for i in range (len (workload)):

      elapsed_time = workload[i] / (avail * math.log (1 + Settings.SNR, 2))
      elapsed_time_accumulated += elapsed_time
      # print ("Elapsed time accumulated (index: " + str (i) + "): " + str (elapsed_time_accumulated))

      if elapsed_time_accumulated > time_passed:
        
        # print ("Accumulated time has surpassed time passed!")
        new_update_task_size = (elapsed_time_accumulated - time_passed) * \
          (avail * math.log (1 + Settings.SNR, 2))
        # print ("New update task size: " + str (new_update_task_size))
        break
    
    if len (workload) == 0 or new_update_task_size == 0.0:
      # empty list
      # print ("Workload is fully completed or empty!")
      return [] 
    
    # print ("Instead of " + str (workload[i]) + ", it will be " + str (new_update_task_size))
    workload[i] = new_update_task_size

    return workload[i:]

  
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


  def _elapsed_workload (cls, workload, time_passed, util):

    elapsed_time_accumulated = 0.0
    new_update_task_size = 0.0
    avail = cls._total - util

    # print ("Time passed: " + str (time_passed))

    for i in range (len (workload)):

      elapsed_time = workload[i] / avail
      elapsed_time_accumulated += elapsed_time
      # print ("Elapsed time accumulated (index: " + str (i) + "): " + str (elapsed_time_accumulated))

      if elapsed_time_accumulated > time_passed:

        # print ("Accumulated time has surpassed time passed!")
        new_update_task_size = (elapsed_time_accumulated - time_passed) * \
          (avail * math.log (1 + Settings.SNR, 2))
        # print ("New update task: " + str (new_update_task_size))
        break
    
    if len (workload) == 0 or new_update_task_size == 0.0:
      # empty list
      # print ("Workload is fully completed or empty!")
      return [] 

    # print ("Instead of " + str (workload[i]) + ", it will be " + str (new_update_task_size))
    workload[i] = new_update_task_size

    return workload[i:]


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
