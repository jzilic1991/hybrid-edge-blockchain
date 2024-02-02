import math
import random
from abc import ABC, abstractmethod

from util import ResponseTime, Settings, Util, CommDirection
from task import Task


# Template method pattern
class EdgeQueue (ABC):


  def __init__ (self, total, direction):

    self._total = total
    self._direction = direction
    self._workload = list ()


  def est_lat (cls, sites, task):

    workload = cls._est_arriv (sites)
    util = cls._est_util (workload)
    
    return cls._est_wait_time (workload, util) + cls._srv_time (task, util)


  def act_lat (cls, sites, task):

    cls._workload.append (cls._act_arriv (sites, task))
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
        
      # remote nodes generate workloads for task execution or task delivery
      if (cls._direction == CommDirection.DOWNLINK and Util.is_remote (site.get_node_type ())) or \
        (cls._direction == CommDirection.UPLINK and not Util.is_remote (site.get_node_type ())):
          
        workload.append (site.get_arrival_rate () * site.get_exp_rate ())

    print ("Estimated workloads: " + str (workload))
    
    return workload


  def _act_arriv (cls, sites, task):

    workload = list ()

    for site in sites:

      # remote nodes generate workloads for task execution or task delivery
      if (cls._direction == CommDirection.DOWNLINK and Util.is_remote (site.get_node_type ())) or \
          (cls._direction == CommDirection.UPLINK and not Util.is_remote (site.get_node_type ())):
          
        workload.append (site.gen_workload ())

    workload.append (task)
    workload = random.shuffle (workload)
    print ("Actual workload: " + str (workload))

    return workload


  def _est_wait_time (cls, workload, util):

    return sum (workload) / (cls._total - util)


  def _act_wait_time (cls, util):

    k = None
    wait = 0.0
    
    for i in range (len (cls._workload)):

      if type (cls._workload[i]) == Task:

        k = i
        break

    return sum (cls._workload[:(k - 1)]) / (cls._total - util)
        

  def _srv_time (cls, task, util):

    avail = cls._total - util

    return task.get_data_in () / (avail * math.log (1 + Settings.SNR, 2))




class CompQueue (EdgeQueue):

  def _est_arriv (cls, site):

    return [site[0].get_arrival_rate () * site[0].get_exp_rate ()]
  

  def _act_arriv (cls, site, task):

    return [site[0].gen_workload (), task]


  def _est_wait_time (cls, workload, util):

    return sum (workload) / (1 - util)


  def _act_wait_time (cls, util):

    k = None
    wait = 0.0
    
    for i in range (len (cls._workload)):

      if type (cls._workload[i]) == Task:

        k = i
        break

    return sum (cls._workload[:(k - 1)]) / (1 - util)


  def _srv_time (cls, task, util):

    return task.get_mi () / (cls._total - util)      
