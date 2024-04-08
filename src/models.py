import math

from util import MeasureUnits, ResponseTime, EnergyConsum, \
  NodeTypes, PowerConsum, NetLinkTypes, Settings, Util, Prices


class Model (object):

  @classmethod
  def bw_consum (cls, task, cand_n, curr_n, topology):

    if cand_n.get_n_id() != curr_n.get_n_id():
      name = cls.__key_for_topology_access (cand_n.get_n_id (), \
        curr_n.get_n_id (), topology)

      if name == None:

        return math.inf

      return (task.get_data_in() * MeasureUnits.KILOBYTE) / \
            (topology[name]['bw'] * MeasureUnits.KILOBYTE_PER_SECOND)

    return 0.0


  @classmethod
  def task_rsp_time (cls, task, cand_n, curr_n, topology):
        
    if cand_n.get_n_id () == curr_n.get_n_id ():

      comp_time = cls.__comp_time(task, cand_n)
      return ResponseTime (comp_time, 0, 0, comp_time)

    uplink_time = cls.__uplink_time (cls, task, cand_n, curr_n, topology)
    comp_time = cls.__comp_time(task, cand_n)
    
    if not task.get_out_edges():
  
      downlink_time = cls.__downlink_time (cls, task, \
        cand_n, curr_n, topology)
        
    else:

      downlink_time = 0
                
    return ResponseTime (comp_time, downlink_time, uplink_time, \
            uplink_time + comp_time + downlink_time)


  @classmethod
  def price (cls, task, off_sites, cand_n, curr_n, topology):

    n_d = cand_n.get_node_type ()

    if n_d == NodeTypes.MOBILE:

      return 0.0

    elif n_d == NodeTypes.E_REG or n_d == NodeTypes.E_DATABASE or \
      n_d == NodeTypes.E_COMP:

      t_f = cls.__t_f (cls, off_sites, topology)

      return (t_f / Settings.ETA) - math.sqrt ((Settings.ETA * \
        cls.__cloud_pr (cls, task, cand_n) + t_f) / Settings.ETA ** 2 * \
        cls.__edge_min_rt (cls, task, off_sites, curr_n, topology)) 

    elif n_d == NodeTypes.CLOUD:

      return cls.__cloud_pr (cls, task, cand_n)

    raise ValueError ("Resource pricing does not recognize node type! " + str (n_d))


  @classmethod
  def task_e_consum (cls, task_rsp_time, cand_n, curr_n):
        
    uplink_time_power = 0.0
    execution_time_power = 0.0
    downlink_time_power = 0.0
    task_energy_consumption = 0.0

    execution_time = task_rsp_time.get_execution()
    downlink_time = task_rsp_time.get_downlink()
    uplink_time = task_rsp_time.get_uplink()
    
    if cand_n.get_node_type() == NodeTypes.MOBILE and\
      curr_n.get_node_type() == NodeTypes.MOBILE:
      execution_time_power = cls.__comp_e_consum(execution_time)
      task_energy_consumption = uplink_time_power + \
        execution_time_power + downlink_time_power

    # use case: mobile device -> Edge/Cloud servers
    elif cand_n.get_node_type() != NodeTypes.MOBILE and\
      curr_n.get_node_type() == NodeTypes.MOBILE:
      uplink_time_power = cls.__uplink_e_consum(uplink_time)
      execution_time_power = cls.__idle_e_consum(execution_time)
      downlink_time_power = cls.__downlink_e_consum(downlink_time)
      task_energy_consumption = cls.__offload_e_consum_uplink \
        (cls, uplink_time, execution_time, downlink_time)

    # use case: Cloud/Edge -> Cloud/Edge (successive tasks executed on the same node)
    elif cand_n.get_node_type() != NodeTypes.MOBILE and\
      curr_n.get_node_type() != NodeTypes.MOBILE and\
      cand_n.get_n_id () == curr_n.get_n_id ():
      execution_time_power = cls.__idle_e_consum(execution_time)
      downlink_time_power = cls.__downlink_e_consum(downlink_time)
      task_energy_consumption = cls.__e_consum_remote_exe(cls, execution_time, \
        downlink_time)

    # use case: Cloud/Edge -> Cloud/Edge (successive tasks executed on the different nodes)	
    elif cand_n.get_node_type() != NodeTypes.MOBILE and\
      curr_n.get_node_type() != NodeTypes.MOBILE and\
      cand_n.get_n_id () != curr_n.get_n_id ():
      execution_time_power = cls.__idle_e_consum(uplink_time + execution_time)
      downlink_time_power = cls.__downlink_e_consum(downlink_time)
      task_energy_consumption = cls.__e_consum_remote_exe\
        (cls, uplink_time + execution_time, downlink_time)

    # use case: Cloud/Edge -> mobile device
    elif cand_n.get_node_type() == NodeTypes.MOBILE and\
      curr_n.get_node_type () != NodeTypes.MOBILE:
      execution_time_power = cls.__comp_e_consum(execution_time)
      downlink_time_power = cls.__downlink_e_consum(uplink_time)
      task_energy_consumption = cls.__offload_e_consum_downlink(cls, \
        uplink_time, execution_time)

    return EnergyConsum (execution_time_power, downlink_time_power, \
      uplink_time_power, task_energy_consumption)


  @classmethod
  def fail_cost (cls, cand_n, curr_n):
        
    time_cost = Settings.OFFLOADING_FAILURE_DETECTION_TIME
    cost_rsp_time = ResponseTime (0.0, 0.0, 0.0, 0.0)
    cost_energy_consum = EnergyConsum (0.0, 0.0, 0.0, 0.0)
    # cost_rewards = 0

    if cand_n.get_node_type () != NodeTypes.MOBILE and \
      curr_n.get_node_type () != NodeTypes.MOBILE:
      cost_rsp_time = ResponseTime (time_cost, 0.0, 0.0, time_cost)
      cost_energy_consum = cls.task_e_consum \
        (cost_rsp_time, cand_n, curr_n)
      # task_time_reward = cls.__task_rsp_time_rwd \
      # 	(cost_rsp_time.get_task_overall())
      # task_energy_reward = cls.__task_e_consum_rwd \
      # 	(cost_energy_consum.get_task_overall())
      # cost_rewards = cls.__overall_task_rwd \
      # 	(task_time_reward, task_energy_reward)

    elif cand_n.get_node_type () == NodeTypes.MOBILE and \
      curr_n.get_node_type () != NodeTypes.MOBILE:
      cost_rsp_time = ResponseTime (0.0, time_cost, 0.0, time_cost)
      cost_energy_consum = cls.task_e_consum (cost_rsp_time, cand_n, curr_n)
      # task_time_reward = cls.__task_rsp_time_rwd \
      # 	(cost_rsp_time.get_task_overall())
      # task_energy_reward = cls.__task_e_consum_rwd \
      # 	(energy_consum.get_task_overall())
      # cost_rewards = cls.__overall_task_rwd \
      # 	(task_time_reward, task_energy_reward)

    elif cand_n.get_node_type () != NodeTypes.MOBILE and \
      curr_n.get_node_type () == NodeTypes.MOBILE:
      cost_rsp_time = ResponseTime (0.0, 0.0, time_cost, time_cost)
      cost_energy_consum = cls.task_e_consum (cost_rsp_time, cand_n, curr_n)
      # task_time_reward = cls.__task_rsp_time_rwd \
      # 	(cost_rsp_time.get_task_overall())
      # task_energy_reward = cls.__task_e_consum_rwd \
      # 	(cost_energy_consum.get_task_overall())
      # cost_rewards = cls.__overall_task_rwd \
      # 	(task_time_reward, task_energy_reward)

    # return (cost_rsp_time, cost_energy_consum, cost_rewards)
    return (cost_rsp_time.get_overall (), cost_energy_consum.get_overall ())


  @classmethod
  def queue_waiting_time (cls, task, top_k_sites):

    wait_times = dict ()

    for off_site in top_k_sites:

      wait_times[off_site] = round (cls.__comp_time (task, off_site), 3)

    return wait_times


  @classmethod
  def task_rsp_time_rwd (cls, task_completion_time):

    if task_completion_time == 0.0:
      return 0.0

    print ("Task completion time: " + str (task_completion_time))
    return 1 / (1 + math.exp(task_completion_time))


  @classmethod
  def task_e_consum_rwd (cls, task_energy_consumption):

    if task_energy_consumption == 0.0:
      return 0.0

    return 1 / (1 + math.exp(task_energy_consumption))


  @classmethod
  def task_price_rwd (cls, price):

    if price == 0.0:
      return 0.0

    return 1 / (1 + math.exp(price))


  @classmethod
  def overall_task_rwd (cls, time_reward, energy_reward): #, price_reward):

    return (0.5 * time_reward) + (0.5 * energy_reward) #+ (0.34 * price_reward)


  def __uplink_time (cls, task, cand_n, curr_n, topology):

    name = cls.__key_for_topology_access (cand_n.get_n_id (), \
      curr_n.get_n_id (), topology)

    if name == None:

      return math.inf

    bw = topology[name]['bw']
    lat = topology[name]['lat']

    if topology[name]['type'] == NetLinkTypes.WIRELESS:

      return (task.get_data_in() * MeasureUnits.KILOBYTE) / \
        ((bw * MeasureUnits.KILOBYTE_PER_SECOND) * math.log (1 + Settings.SNR)) + \
        (lat / MeasureUnits.THOUSAND_MS)
        
    return ((task.get_data_in() * MeasureUnits.KILOBYTE) / \
      (bw * MeasureUnits.KILOBYTE_PER_SECOND)) + \
      (lat / MeasureUnits.THOUSAND_MS)


  def __downlink_time (cls, task, cand_n, curr_n, topology):

    if cand_n.get_n_id () == curr_n.get_n_id ():

      return 0.0

    name = cls.__key_for_topology_access (cand_n.get_n_id (), \
      curr_n.get_n_id (), topology)

    if name == None:

      return math.inf

    bw = topology[name]['bw'] 
    lat = topology[name]['lat']

    if topology[name]['type'] == NetLinkTypes.WIRELESS:

      return (task.get_data_out() * MeasureUnits.KILOBYTE) / \
        ((bw * MeasureUnits.KILOBYTE_PER_SECOND) * math.log (1 + Settings.SNR)) + \
        (lat / MeasureUnits.THOUSAND_MS)
        
    return ((task.get_data_out() * MeasureUnits.KILOBYTE) / \
      (bw * MeasureUnits.KILOBYTE_PER_SECOND)) + \
        (lat / MeasureUnits.THOUSAND_MS)


  def __comp_time (task, curr_n):
        
    return (task.get_mi () / (curr_n.get_mips () * curr_n.get_cores ())) + curr_n.get_cpu_consum ()


  def __cloud_pr (cls, task, cand_n):

    return cls.__cloud_pr_cpu (cls, task, cand_n) + cls.__cloud_pr_stor (cls, task)


  def __cloud_pr_cpu (cls, task, curr_n):

    return ((task.get_mi () / (curr_n.get_mips () * curr_n.get_cores ())) / MeasureUnits.HOUR_IN_SEC) \
       * Prices.CPU_PER_HOUR


  def __cloud_pr_stor (cls, task):

    return (((task.get_data_in () + task.get_data_out ()) * MeasureUnits.KILOBYTE) / MeasureUnits.GIGABYTES) \
       * Prices.STOR_PER_GB


  def __cloud_t_f (cls, c_sites, m_site, topology):

    t_f = 0.0

    for site in c_sites:

      name = cls.__key_for_topology_access (site.get_n_id (), \
        m_site.get_n_id (), topology)

      if name == None:

        return math.inf

      t_f = t_f + ((topology[name]['lat'] / MeasureUnits.THOUSAND_MS) / len (c_sites)) + (1 / site.get_cores ())

    return t_f


  def __edge_t_f (cls, e_sites, m_site, topology):

    t_f = 0.0

    for site in e_sites:

      name = cls.__key_for_topology_access (site.get_n_id (), \
        m_site.get_n_id (), topology)

      if name == None:

        return math.inf

      t_f = t_f + ((topology[name]['lat'] / MeasureUnits.THOUSAND_MS) / len (e_sites))

    return t_f


  def __edge_min_rt (cls, task, off_sites, curr_n, topology):

    e_sites = Util.get_edge_sites (off_sites)
    min_rt = 0.0

    for cand_n in e_sites:

      t_rsp_time = cls.task_rsp_time (task, cand_n, curr_n, topology).get_overall ()
      if min_rt == 0.0:

        min_rt = t_rsp_time

      elif min_rt > t_rsp_time:

        min_rt = t_rsp_time

    # print ("Edge min RT = " + str (min_rt))
    return min_rt


  def __t_f (cls, off_sites, topology):

    c_sites = Util.get_cloud_sites (off_sites)
    e_sites = Util.get_edge_sites (off_sites)
    m_site = Util.get_mob_site (off_sites)

    return cls.__cloud_t_f (cls, c_sites, m_site, topology) - \
      cls.__edge_t_f (cls, e_sites, m_site, topology)


  def __offload_e_consum_downlink (cls, downlink_time, execution_time):
        
    return cls.__downlink_e_consum (downlink_time) + \
      cls.__comp_e_consum(execution_time)

    
  def __offload_e_consum_uplink (cls, uplink_time, idle_time, downlink_time):
        
    return cls.__uplink_e_consum (uplink_time) + cls.__idle_e_consum (idle_time) \
      + cls.__downlink_e_consum(downlink_time)
    
    
  def __e_consum_remote_exe (cls, remote_execution_time, downlink_time):
        
    return cls.__idle_e_consum(remote_execution_time) + \
      cls.__downlink_e_consum (downlink_time)

    
  def __uplink_e_consum (uplink_time):
        
    return uplink_time * PowerConsum.UPLINK


  def __downlink_e_consum (downlink_time):
        
    return downlink_time * PowerConsum.DOWNLINK


  def __comp_e_consum(execution_time):
        
    return execution_time * PowerConsum.LOCAL

    
  def __idle_e_consum (idle_time):
        
    return idle_time * PowerConsum.IDLE


  def __key_for_topology_access (f_name, s_name, topology):

    f_alt_name = f_name + '-' + s_name
    s_alt_name = s_name + '-' + f_name
    name = ""

    if f_alt_name in topology:
      name = f_alt_name

    else:
      name = s_alt_name

    if name in topology:

      return name

    else:

      return None

