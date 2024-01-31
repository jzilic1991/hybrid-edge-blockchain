import math
from abc import ABC, abstractmethod

from util import ResponseTime, Settings, Util, CommDirection



# Template method pattern
class EdgeQueue (ABC):

  def __init__ (self, total, direction):

    self._total = total
    self._util = 0.0
    self._workload = 0.0
    self._latency = 0.0
    self._direction = direction

  
  def get_utilization (cls):

    return cls._util


  def est_latency (cls, task):

    # waiting time is depended on current overall workload while service time depends on target offloaded task
    total_latency = cls._est_wait_time () + cls._est_srv_time (task)

    return ResponseTime (total_latency, 0, 0, total_latency)


  def _est_util (cls, workloads):

    util = 0.0

    for w in workloads:

      util += w / cls._total

    cls._util = util

  
  def arrival (cls):

    pass


  def _est_wait_time (cls):

    pass


  def _est_srv_time (cls, task):

    pass




class CommQueue (EdgeQueue):
  
  def arrival (cls, infra):

    cls._workload = 0.0
    workloads = list ()

    for site in infra:
        
      # remote nodes generate workloads for task execution or task delivery
      if cls._direction == CommDirection.DOWNLINK \
        and Util.is_remote (site.get_node_type ()):
          
        workloads.append (site.gen_workload (2, 3))

        # mobile workload
      elif cls._direction == CommDirection.UPLINK \
        and not Util.is_remote (site.get_node_type ()):
          
        workloads.append (site.gen_workload (2, 3))

    # sum all workloads and compute current utlization factor 
    cls._workload = sum (workloads)
    cls._est_util (workloads)


  def _est_wait_time (cls):

    return cls._workload / (cls._total - cls._util)


  def _est_srv_time (cls, task):

    avail = cls._total - cls._util

    return task.get_data_in () / (avail * math.log (1 + Settings.SNR, 2))




class CompQueue (EdgeQueue):

  # infra should be only a single device
  def arrival (cls, infra):

    # argument be placed in a list
    cls._est_util ([infra.gen_workload (2, 3)]) 


  def _est_wait_time (cls):

    return cls._workload / (1 - cls._util)


  def _est_srv_time (cls, task):

    return task.get_mi () / cls._total      
