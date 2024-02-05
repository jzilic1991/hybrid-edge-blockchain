import math
import random
from abc import ABC, abstractmethod

from util import ResponseTime, Settings, Util, CommDirection
from task import Task


# Template method pattern
class EdgeQueue (ABC):


  def __init__ (self, total, comm_direct = None, site_name = None):

    self._total = total
    self._comm_direct = comm_direct
    self._site_name = site_name
    self._workload = list ()


  def est_lat (cls, sites, task):

    workload = cls._est_arriv (sites)
    util = cls._est_util (workload)
    
    return cls._est_wait_time (workload, util) + cls._srv_time (task, util)


  def act_lat (cls, sites, task):

    cls._workload.extend (cls._act_arriv (sites, task))
    util = cls._act_util (task)
    
    return cls._act_wait_time (util) + cls._srv_time (task, util)


  def _est_util (cls, workload):

    util = 0.0

    for w in workload:
      
      util += w / cls._total

    return util


  def _act_util (cls, task):

    util = 0.0

    for w in cls._workload:

      if type (w) == float:
        
        util += w / cls._total
        continue

      util += task.get_mi () / cls._total
    
    return util


  def _est_arriv (cls, sites):

    pass

  
  def _act_arriv (cls, sites, task):

    pass


  def _est_wait_time (cls, workload, util):

    pass


  def _act_wait_time (cls, util):

    pass


  def _srv_time (cls, task, util):

    pass




class CommQueue (EdgeQueue):

  def _est_arriv (cls, sites):

    workload = list ()

    for site in sites:
        
      # remote nodes generate workloads for task execution or task delivery queues
      if (cls._comm_direct == CommDirection.DOWNLINK and Util.is_remote (site.get_node_type ())) or \
        (cls._comm_direct == CommDirection.UPLINK and not Util.is_remote (site.get_node_type ())):
          
        workload.append (site.get_arrival_rate () * site.get_exp_rate ())
    
    return workload


  def _act_arriv (cls, sites, task):

    workload = list ()

    for site in sites:
      
      # remote nodes generate workloads for task execution or task delivery queues
      if (cls._comm_direct == CommDirection.DOWNLINK and Util.is_remote (site.get_node_type ())) or \
          (cls._comm_direct == CommDirection.UPLINK and not Util.is_remote (site.get_node_type ())):
        
        # workload.append (site.gen_workload ())
        numb_of_tasks = site.gen_numb_of_tasks ()

        for i in range (numb_of_tasks):
          
          workload.append (site.gen_task_size ())

    workload.append (task)
    random.shuffle (workload)
    print (str (cls._comm_direct) + " comm queue actual workload: " + str (workload))

    return workload


  def _est_wait_time (cls, workload, util):

    return sum (workload) / (cls._total - util)


  def _act_wait_time (cls, util):

    for i in range (len (cls._workload)):

      if type (cls._workload[i]) == Task:
        
        if i != 0:
          
          return sum (cls._workload[:(i - 1)]) / (cls._total - util)

        return 0.0

    raise ValueError ("Task should be present in the workload list: " + str (cls._workload))
        

  def _srv_time (cls, task, util):

    avail = cls._total - util

    return task.get_data_in () / (avail * math.log (1 + Settings.SNR, 2))




class CompQueue (EdgeQueue):

  def _est_arriv (cls, site):

    return [site[0].get_arrival_rate () * site[0].get_exp_rate ()]
  

  def _act_arriv (cls, site, task):

    workload = list ()
    numb_of_tasks = site[0].gen_numb_of_tasks ()

    for i in range (numb_of_tasks):
      
      workload.append (site[0].gen_task_size ())

    workload.append (task)
    random.shuffle (workload)
    print ("Comp queue actual workload: " + str (workload))

    return workload


  def _est_wait_time (cls, workload, util):

    return sum (workload) / (1 - util)


  def _act_wait_time (cls, util):
    
    for i in range (len (cls._workload)):

      if type (cls._workload[i]) == Task:
        
        if i != 0:
          
          return sum (cls._workload[:(i - 1)]) / (1 - util)

        return 0.0

    raise ValueError ("Task was not found in the workload: " + str (cls._workload))


  def _srv_time (cls, task, util):

    return task.get_mi () / (cls._total - util)      
