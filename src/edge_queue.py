import math
from abc import ABC, abstractmethod

from util import ResponseTime, Settings


class EdgeQueue (ABC):

  def __init__ (self, total):

    self._total = total
    self._util = 0.0
    self._workload = 0.0
    self._latency = 0.0


  def arrival (cls, mds, group):

    cls._workload = 0.0
    workloads = list ()

    # compute complete workload of all mobile devices
    for md in mds:

      workloads.append (md.gen_workload (2, 3))

    cls._workload = sum (workloads)

    # compute utilization factor
    cls._est_util (workloads)

  
  def get_utilization (cls):

    return cls._util


  def est_latency (cls, task):

    # waiting time is depended on current overall workload while service time depends on target offloaded task
    total_latency = cls._est_wait_time () + cls._est_srv_time (task)

    return ResponseTime (total_latency, 0, 0, total_latency)


  def _est_util (cls, workloads):

    pass


  def _est_wait_time (cls):

    pass


  def _est_srv_time (cls, task):

    pass


class CommQueue (EdgeQueue):
  
  def _est_util (cls, workloads):

    util = 0.0

    for w in workloads:

      util += w / cls._total

    cls._util = util


  def _est_wait_time (cls):

    return cls._workload / (cls._total - cls._util)


  def _est_srv_time (cls, task):

    avail = cls._total - cls._util

    return task.get_data_in () / (avail * math.log (1 + Settings.SNR, 2))