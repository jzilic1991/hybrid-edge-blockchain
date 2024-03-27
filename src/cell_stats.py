import numpy as np


class CellStats:

  def __init__(self, cell_name):

    self._id = cell_name
    self._off_dist_samp = dict ()   # of dicts per offloading site key per sampling
    self._off_fail_samp = dict ()   # of scalars per sampling
    self._constr_viol = dict ()     # 


  def get_off_dist_samp (cls):

    return cls._off_dist_samp


  def get_off_fail_samp (cls):

    return cls._off_fail_samp


  def get_constr_viol_samp (cls):

    return cls._constr_viol


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

    for key, _ in cls._constr_viol.items ():
      for i in range (len (cls._constr_viol[key])):
        if cls._off_dist_samp[key][i] != 0:
          constr_viol.append (round (cls._constr_viol[key][i] / cls._off_dist_samp[key][i] \
            * 100, 3))

        else:
          constr_viol.append (0.0)

    if len (constr_viol) == 0:
      return "Average constraint violation rate (percentage) is 0.0"

    else:
      return "Average constraint violation rate (percentage) is " + \
        str (round (sum (constr_viol) / len (constr_viol), 3))


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


  def get_all (cls):

    return "########### CELL " + str (cls._id) + " #############\n" + cls.get_avg_off_dist () + '\n' + \
      cls.get_avg_off_fail_dist () + '\n' + \
      cls.get_avg_off_fail () + "\n" + cls.get_avg_constr_viol_dist () + '\n' + \
      cls.get_avg_constr_viol () + "\n"


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
