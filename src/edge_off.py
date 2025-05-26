import random
import datetime
from threading import Thread

from smt_ode import SmtOde
from sq_ode import SqOde
from mdp_ode import MdpOde
from mob_app_profiler import MobileAppProfiler
from res_mon import ResourceMonitor
from util import Util, Settings


class EdgeOffloading (Thread):

  def __init__ (
    self, 
    req_q, 
    rsp_q, 
    exe, 
    samp, 
    app_name, 
    con_delay, 
    scala, 
    locs,
    alpha = None,
    beta = None,
    gamma = None,
    k = None,
    suffix = None,
    disable_trace_log = True):

    Thread.__init__ (self)

    self._r_mon = ResourceMonitor (scala)
    self._m_app_prof = MobileAppProfiler () 
    self._s_ode = None
    self._req_q = req_q
    self._rsp_q = rsp_q
    self._exe = exe
    self._samp = samp
    self._app_name = app_name
    self._con_delay = con_delay
    self._log = None
    self._cell_number = 0
    # user moves to another cell location after certain number of applications excutions
    # it only works when number of executions is higher than number of locations
    # the division result should be a integer
    self._user_move = self._exe / locs
    # print ("User move: " + str (self._user_move))
    # Sensitivity analysis params (FRESCO only)
    self.alpha = alpha if alpha is not None else 0.3
    self.beta = beta if beta is not None else 0.3
    self.gamma = gamma if gamma is not None else 0.4
    self.k = k if k is not None else 5
    self.suffix = suffix if suffix is not None else 0
    self.disable_trace_log = disable_trace_log

  def log_sensitivity_summary(self, filename):
    stats = self._s_ode._stats
    cell_stats = self._s_ode._cell_stats

    avg_latency = stats.get_avg_rsp_time_value()
    total_energy = stats.get_sum_e_consum()
    total_cost = stats.get_sum_res_pr()
    qos_violation = stats.get_avg_qos_viol_value()

    avg_dec_time = 0.0
    if cell_stats:
        avg_dec_time = sum([cell.get_avg_overhead() for cell in cell_stats.values()]) / len(cell_stats)

    score = self.alpha * avg_latency + self.beta * total_cost + self.gamma * total_energy

    with open(filename, "w") as f:
        f.write(f"{self.suffix},{self.alpha},{self.beta},{self.gamma},{self.k},"
                f"{avg_latency},{total_energy},{total_cost},{avg_dec_time},{qos_violation},{score}\n")

    print(f"[LOGGED] ID={self.suffix}: α={self.alpha}, β={self.beta}, γ={self.gamma}, k={self.k} → "
          f"Score={score:.3f}, Latency={avg_latency}, Energy={total_energy}, "
          f"Cost={total_cost}, QoS Violations={qos_violation}%, Decision Time={avg_dec_time}")


  def deploy_fresco_ode (self):
    self._s_ode = SmtOde ('FRESCO', 
        self._r_mon.get_md (self._cell_number), 
        self._r_mon.get_md (self._cell_number), \
        self._app_name, 
        True, 
        self._con_delay,
        alpha = self.alpha,
        beta = self.beta,
        gamma = self.gamma,
        k = self.k,
        disable_trace_log = self.disable_trace_log)
    #print(f"[FRESCO CONFIG] α={self.alpha}, β={self.beta}, γ={self.gamma}, k={self.k}")


  def deploy_smt_ode (self):
    self._s_ode = SmtOde ('MINLP', self._r_mon.get_md (self._cell_number), self._r_mon.get_md (self._cell_number), \
      self._app_name, False, self._con_delay)


  def deploy_sq_ode (self):
    self._s_ode = SqOde ('SQ_MOBILE_EDGE', self._r_mon.get_md (self._cell_number), self._r_mon.get_md (self._cell_number), self._app_name, \
      self._con_delay)


  def deploy_mdp_ode (self):
    self._s_ode = MdpOde ('MDP', self._r_mon.get_md (self._cell_number), self._r_mon.get_md (self._cell_number), \
      self._app_name, self._con_delay)


  def run (self):
    # logging but after ODE is deployed
    if not self.disable_trace_log:
        self._log = self._s_ode.get_logger ()
    
    off_sites = self.__update_and_register_off_sites ()
    # deploy and run mobile application
    app = self._m_app_prof.dep_app (self._app_name)
    app.run ()

    # setting cell statistics (this is updated after each cell move)
    self._s_ode.set_cell_stats (self._r_mon.get_cell_name ())

    epoch_cnt = 0 # counts task offloadings
    exe_cnt = 0   # counts application executions
    samp_cnt = 0  # counts samples
    period_cnt = 0 # counts number of task offloadings within single time period in cell location
    time_period = self.__compute_time_period (app.get_num_of_tasks ())
    timestamp = 0.0
    prev_progress = 0
    curr_progress = 0
    con_delay = 0 # consensus delay constraint
    task_n_delay = "" # delay counter (counting epochs)
    off_transactions = list ()

    # self._log.w ("APP EXECUTION No." + str (exe_cnt + 1))
    # self._log.w ("SAMPLE No." + str (samp_cnt + 1))

    print("**************** PROGRESS " + self._s_ode.get_name() + " (ID = " + str(self.suffix) + ") ****************")
    print(str(prev_progress) + "% - " + str(datetime.datetime.utcnow()) + "(ID = " + str(self.suffix) + ")")

    while True:
      (curr_progress, prev_progress) = self.__print_progress (exe_cnt, samp_cnt, \
        curr_progress, prev_progress)

      tasks = app.get_ready_tasks ()
      timestamp = round (time_period * period_cnt, 3)

      # when all application tasks are completeid
      # print ("User move: " + str (self._user_move))
      # print ("Execution count: " + str (exe_cnt))
      # print (str (len (tasks)) + " to offload!")
      if len (tasks) == 0:
        # deploy and run mobile application
        app = self._m_app_prof.dep_app (self._app_name)
        # update current site of task exeuction when previous app execution is completed
        self._s_ode.set_curr_node (Util.get_mob_site (off_sites))
        app.run ()
        exe_cnt = exe_cnt + 1
        
        # evaluate application response time against application QoS deadline
        self._s_ode.app_exc_done (app.get_qos ())
        
        # cell mover flag for indicating is cell location has changed
        # if yes then reputation update is not needed
        # it is a fix solution for sending a new offloading transaction when previous offloading transaction is still pending 
        cell_mover = False

        # when certain number of application executions are completed 
        # then mobile device moves to another cell location and 
        # new availability datasets are loaded per offloading site
        if exe_cnt % self._user_move == 0:
          period_cnt = 0
          cell_mover = True

          # summarize cell statistics (off distro, off fails, constr viols, avail distro) 
          self._s_ode.summarize_cell_stats (self._cell_number, \
            self.__get_avail_distro (off_sites))

          # update cell number of new switched cell location and get offloading sites of new cell 
          # self._cell_number = int (exe_cnt / self._user_move)
          self._cell_number += 1
          off_sites = self.__update_and_register_off_sites ()
          # set new cell statistics for a new cell
          self._s_ode.set_cell_stats (self._cell_number)
          # update current site of task exeuction when switching cells
          self._s_ode.set_curr_node (Util.get_mob_site (off_sites))

        # self._log.w ("APP EXECUTION No." + str (exe_cnt + 1))
        
        if not cell_mover:
          # update reputation after each application execution and reset transaction list
          # print ("############## UPDATING TRANSACTIONS ###############")
          # print ("Transactions: " + str (off_transactions))
          self._req_q.put (('update', off_transactions))
          off_transactions = list ()
        
        continue

      # consensus delay
      if tasks[0].get_name == task_n_delay:
        con_delay = con_delay + 1

      # incrementing epoch (i.e. task offloading) and period counter (i.e. epochs within same time period)
      epoch_cnt = epoch_cnt + 1
      period_cnt = period_cnt + 1
      # self._log.w ('Time epoch ' + str (epoch_cnt) + '.')

      # all executions are completed
      if exe_cnt >= self._exe:
        self._s_ode.summarize (exe_cnt)
        samp_cnt = samp_cnt + 1
        exe_cnt = 0
        self._cell_number = 0

        # if all samples are completed, end the experiment via message queue close
        if samp_cnt == self._samp: 
          self._s_ode.log_stats ()
          # self.__reset_reputation (off_sites)
          self._req_q.put (('close', [site.get_sc_id () for site in off_sites]))
        
          if self._rsp_q.get () == 'confirm':
            # break from the run loop
            break

        # self._log.w ("SAMPLE No." + str (samp_cnt + 1))
        app = self._m_app_prof.dep_app (self._app_name)
        app.run ()
        # off_sites = self.__reset_reputation (off_sites)
        continue

      # getting updated reputation when consensus is finished after certain delay
      # print ("\n\n\n******************** OFFLOADING TRANSACTION ***************************")
      if con_delay == self._con_delay:
        off_sites = self.__get_reputation (off_sites)
        # self.__print_reputation (off_sites)
        con_delay = 0
        task_n_delay = tasks[0].get_name ()

      # off_sites = self.__update_behav (off_sites, exe_cnt)
      trxs = self._s_ode.offload (tasks, off_sites, timestamp, app.get_name (), app.get_qos (), self._r_mon.get_cell_name ())
      off_transactions += trxs

      # update workload after task offloading
      curr_n = self._s_ode.get_curr_node ()
      for site in off_sites:
          if site != curr_n:
              site.workload_update (self._s_ode.get_last_rsp_time ())

      if not off_transactions:
        exe_cnt = self._exe
        continue


  # printing reputation score values per offloading site
  def __print_reputation (self, off_sites):
    trace = "################### REPUTATION SCORES ##################\n"

    for site in off_sites:
      if site.get_reputation () != 0.5:
        trace += "####### SC ID: " + str (site.get_sc_id ()) + ": " + \
          str (site.get_reputation ()) + "######## | "
        continue

      trace += "SC ID: " + str (site.get_sc_id ()) + ": " + str (site.get_reputation ()) + " | "

    print (trace)


  def __get_avail_distro (self, off_sites):

    avail_distro = dict ()
  
    for site in off_sites:
      # avail distro is stored by node prototype key
      node_proto = site.get_node_prototype ()
      if node_proto in avail_distro:
        continue

      avail_distro[node_proto] = site.get_avail ()

    return avail_distro


  def __update_and_register_off_sites (self):
    off_sites = self._r_mon.get_cell (self._cell_number)
    # register offloading sites of new switched cell location
    off_sites = self.__register_nodes (off_sites)
    # check if MDP decision engine is deployed, if yes, then update matrices with offloading site list
    if isinstance (self._s_ode, MdpOde):
      self._s_ode.update_matrices (off_sites)

    return off_sites


  def __compute_time_period (self, num_of_tasks):

    return round (1 / (num_of_tasks * (self._user_move)), 3)


  def __print_progress (self, exe_cnt, samp_cnt, curr_progress, prev_progress):

    prev_progress = curr_progress
    curr_progress = round((exe_cnt + (samp_cnt * self._exe)) / \
      (self._samp * self._exe) * 100)

    if curr_progress != prev_progress and (curr_progress % \
      Settings.PROGRESS_REPORT_INTERVAL == 0):
      print(str(curr_progress) + "% - " + str(datetime.datetime.utcnow()) + " (ID = " + str(self.suffix) + ")")

    return (curr_progress, prev_progress)


  def __register_nodes (self, off_sites):

    names = [site.get_n_id () for site in off_sites]
    print("Registration of " + str (len (names)) + " nodes (Cell ID = " + str (self._cell_number) + ") -> [ODE ID = " + str(self.suffix) + "]")
    self._req_q.put (('reg', names))
    reg_nodes = self._rsp_q.get ()
  
    if reg_nodes[0] == 'reg_rsp':
      for ele in reg_nodes[1]:
        for site in off_sites:
          if ele['name'] == site.get_n_id ():
            site.set_sc_id (ele['id'])
            # print (site.get_n_id () + " has availability of " + str (site.get_avail ()))
            # print ("SC ID is a " + str (ele['id']))
            break

    # measuring offloading decision time 
    self._s_ode.start_measuring_overhead ()
    
    return off_sites


  def __get_reputation (self, off_sites):

    sc_ids = [site.get_sc_id () for site in off_sites]
    self._req_q.put (('get', sc_ids))
    get_msg = self._rsp_q.get ()

    if get_msg[0] == 'get_rsp':
      for site_rep in get_msg[1]:
        for site in off_sites:
          if site_rep[0] == site.get_sc_id ():
            site.set_reputation (site_rep[1])
            # self._log.w (site.get_n_id () + " reputation is " + str (site.get_reputation ()))

    return off_sites


  def __print_setup (self, off_sites, app):

    app.print_entire_config ()

    for off_site in off_sites:
      off_site.print_system_config ()


  def __reset_reputation (self, off_sites):

    sc_ids = [site.get_sc_id () for site in off_sites]
    self._req_q.put (('reset', sc_ids))
    reset_msg = self._rsp_q.get ()

    if reset_msg[0] == 'reset_rsp':
      for site_rep in reset_msg[1]:
        for site in off_sites:
          if site_rep['id'] == site.get_sc_id ():
            site.set_reputation (site_rep['score'])
            # print (site.get_n_id () + " reputation reseted on " + str (site.get_reputation ()))
            # self._log.w (site.get_n_id () + " reputation reseted on " + str (site.get_reputation ()))
    
    return off_sites
