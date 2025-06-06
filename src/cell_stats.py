import numpy as np


class CellStats:

  def __init__(self, cell_name):

    self._id = cell_name
    self._off_dist_samp = dict ()   # of dicts per offloading site key per sampling
    self._off_fail_samp = dict ()   # of scalars per sampling
    self._constr_viol = dict ()     # 
    self._avail_distros = dict ()    # avaialability distribution per node prototype
    self._overhead = list ()
    self._infra_size = 0


  def get_avg_overhead(self):
      if not self._overhead:
          return (0.0)
      return round(sum(self._overhead) / len(self._overhead), 3)


  def get_off_dist_samp (cls):
    return cls._off_dist_samp


  def get_off_fail_samp (cls):
    return cls._off_fail_samp


  def get_constr_viol_samp (cls):
    return cls._constr_viol


  def get_avail_distro (cls):
    return cls._avail_distro


  def get_avg_off_dist (cls):
    result = dict ()

    for key, val in cls._off_dist_samp.items ():
      result[key] = round (sum (val) / len (val), 2)

    rel_result = dict ()
    all_offloads = sum (result.values ())

    for key, val in result.items ():
      rel_result[key] = round (val / all_offloads, 2) * 100

    return ("Offloading distribution (percentage): " + str (rel_result))


  def get_avg_off_fail (cls):
    off_fail = list ()

    for key, _ in cls._off_fail_samp.items ():
      for i in range (len (cls._off_fail_samp[key])):
        if cls._off_dist_samp[key][i] != 0:
          off_fail.append (round (cls._off_fail_samp[key][i] / cls._off_dist_samp[key][i] \
            * 100, 3))
        else:
          off_fail.append (0.0)

    if len (off_fail) == 0:
      return "Average task failure rate (percentage) is 0.0"
    
    else:
      return "Average task failure rate (percentage) is " + \
        str (round (sum (off_fail) / len (off_fail), 3))


  def get_avg_constr_viol (cls):
    constr_viol = list ()
    off_attempts = list ()

    # print ("Cell ID: " + str (cls._id))
    for key, _ in cls._constr_viol.items (): # key is offloading site name
      for i in range (len (cls._constr_viol[key])): # i index is number of sample
        constr_viol.append (cls._constr_viol[key][i])
        off_attempts.append (cls._off_dist_samp[key][i])

    # print ("Constraint violation list: " + str (constr_viol))
    # print ("Offloading attempts list: " + str (off_attempts))
    
    if not off_attempts:
      return ("Average constraint violation rate 0.0 %")

    return "Average constraint violation rate is " + \
      str (round (sum (constr_viol) / sum (off_attempts) * 100, 3)) + " %" 


  def get_avg_off_fail_dist (cls):
    off_fail = dict ()
    for key, val in cls._off_fail_samp.items ():
      off_fail[key] = round (sum (val) / len (val), 3)

    off_dist = dict ()
    for key, val in cls._off_dist_samp.items ():
      off_dist[key] = round (sum (val) / len (val), 3)

    result = dict ()
    for key in cls._off_fail_samp.keys ():
      if off_dist[key] != 0:
        result[key] = round ((off_fail[key] / off_dist[key]) * 100, 2)
      else:
        result[key] = 0

    return ("Offloading failure distribution (percentage): " + str (result))


  def get_avg_constr_viol_dist (cls):
    constr_viol = dict ()
    for key, val in cls._constr_viol.items ():

      constr_viol[key] = round (sum (val) / len (val), 3)

    off_dist = dict ()
    for key, val in cls._off_dist_samp.items ():

      off_dist[key] = round (sum (val) / len (val), 3)

    result = dict ()
    for key in cls._constr_viol.keys ():
      if off_dist[key] != 0:
        result[key] = round ((constr_viol[key] / off_dist[key]) * 100, 2)
      else:
        result[key] = 0

    return ("Constraint violation distribution (percentage): " + str (result))


  def get_avail_distros (cls):
    return ("Availability distributions (statistically): " + str (cls._avail_distros))


  def get_all (cls):
    overhead_avg = cls.get_avg_overhead()
    return (
        f"########### CELL {cls._id} #############\n"
        f"{cls.get_avail_distros()}\n"
        f"{cls.get_avg_off_dist()}\n"
        f"{cls.get_avg_off_fail_dist()}\n"
        f"{cls.get_avg_off_fail()}\n"
        f"{cls.get_avg_constr_viol_dist()}\n"
        f"{cls.get_avg_constr_viol()}\n"
        f"Offloading decision time overhead: ({cls._infra_size} nodes, {overhead_avg:.6f} s)\n"
    )
    
  def add_off_dist (cls, off_dist_samp):
    for key, val in off_dist_samp.items ():
      if key in cls._off_dist_samp.keys ():
        cls._off_dist_samp[key].append (val)
      else:
        cls._off_dist_samp[key] = [val]


  def add_off_fail (cls, off_fail_samp):

    for key, val in off_fail_samp.items ():
      if key in cls._off_fail_samp.keys ():
        cls._off_fail_samp[key].append (val)
      else:
        cls._off_fail_samp[key] = [val]


  def add_constr_viol (cls, constr_viol):
    for key, val in constr_viol.items ():
      if key in cls._constr_viol.keys ():
        cls._constr_viol[key].append (val)
      else:
        cls._constr_viol[key] = [val]


  def add_overhead (cls, infra_size, overhead):
    cls._overhead.append (overhead)
    cls._infra_size = infra_size

  ### avail_distros - dictionary { key: node prototype => value: mean value 
  ### of avail distro (float) } 
  def set_avail_distros (cls, avail_distros):
    cls._avail_distros = avail_distros
