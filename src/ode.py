import math
from abc import ABC, abstractmethod

from util import Settings, NodePrototypes, ResponseTime
from stats import Stats
from cell_stats import CellStats
from logger import Logger
from models import Model


class OffloadingDecisionEngine(ABC):

    def __init__(self, 
        name, 
        curr_n, 
        md, 
        app_name, 
        con_delay,
        alpha = None,
        beta = None,
        gamma = None,
        k = None,
        disable_trace_log = True):
            
        self._name = name
        self._curr_n = curr_n
        self._md = md

        self._BL = Settings.BATTERY_LF
        self._rsp_time_hist = list ()
        self._e_consum_hist = list ()
        self._res_pr_hist = list ()
        self._off_dist_hist = dict ()
        self._off_fail_hist = dict ()
        self._constr_viol_hist = dict ()
        self._qos_viol_cnt = 0
        self._curr_app_time = 0.0
        self._stats = Stats ()
        self._cell_stats = dict ()       # key (cell name) - value is cell stats class object
        self._measure_off_dec_time = True
        self._log = None
        self._disable_trace_log = disable_trace_log
        if not self._disable_trace_log:
          self._log = Logger(f'logs/sim_traces_{self._name}_{app_name or "random"}.txt', True, 'w')

        self._alpha = alpha if alpha is not None else Settings.W_RT
        self._beta = beta if beta is not None else Settings.W_EC
        self._gamma = gamma if gamma is not None else Settings.W_PR
        self._k = k if k is not None else Settings.K  # use default from config
        
        super().__init__()


    def get_name(self):
        return self._name


    def get_current_site (self):
        return self._curr_n


    def get_md (self):
        return self._md


    def start_measuring_overhead (self):
        self._measure_off_dec_time = True


    def dynamic_t_incentive (self, site, metric, app_name):

        constr = site.get_constr (app_name)
        proc = constr.get_proc ()
        lat = constr.get_lat ()
        deadline = proc + lat
        tmp = round ((deadline - metric['rt']) / deadline, 3) * 1000

        if tmp == math.inf or tmp == -math.inf:
            incentive = 0
        else:
            incentive = int (tmp)

        if incentive >= 0 and incentive <= 1000:
            return incentive

        return 0


    def set_cell_stats (self, cell_name):

        if not cell_name in self._cell_stats:
            self._cell_stats[cell_name] = CellStats (cell_name)


    def app_exc_done (self, qos):

        if qos['rt'] < self._curr_app_time:
            # print ("Application QoS is violated! RT: " + str (self._curr_app_time) + " s, QoS: " + \
            #  str (qos['rt']) + " s")
            self._qos_viol_cnt += 1
        
        self._curr_app_time = 0.0


    def offload (self, tasks, off_sites, timestamp, app_name, qos, cell_name):

        if self._BL <= 0.0:
            return []

        cand_n = None
        t_rsp_time_arr = tuple ()
        t_e_consum_arr = tuple ()
        t_price_arr = tuple ()
        off_transactions = list ()

        # check does offloading site history statistics exists
        self.__check_off_sites (off_sites)
        # print infrastructure failures on offloading sites
        # self.__print_current_failures (off_sites, timestamp)

        # find edge site for timing deadine constraint
        constr = None
        for site in off_sites:
            if site.get_node_prototype () == NodePrototypes.ED or \
                site.get_node_prototype () == NodePrototypes.EC or \
                site.get_node_prototype () == NodePrototypes.ER:

                constr = site.get_constr (app_name)

        for task in tasks:
            t_rsp_time = 0.0
            t_e_consum = 0.0
            t_price = 0.0
            t_fail_cost = 0.0
            e_fail_cost = 0.0
            pr_fail_cost = 0.0

            metrics = self.__compute_metrics (task, off_sites, self._curr_n)

            while True:

                cand_n, values = self.offloading_decision (task, metrics, timestamp, app_name, \
                    constr, qos, cell_name)
                self._off_dist_hist[cand_n.get_node_prototype ()] += 1

                if cand_n.execute (task, timestamp):
                    # t_rsp_time = t_rsp_time + values['rt']
                    # t_e_consum = t_e_consum + values['ec']
                    # t_price = t_price + values['pr']
                    (t_rsp_time, t_e_consum, t_price) = self.__runtime_objectives (task, off_sites, \
                      cand_n, self._curr_n)
                    # print ("Execution is done! Completed task latency is " + str (t_rsp_time))
                    t_rsp_time += t_fail_cost
                    t_e_consum += e_fail_cost
                    t_price += pr_fail_cost
                    t_rsp_time_arr += (t_rsp_time,)
                    t_e_consum_arr += (t_e_consum,)
                    t_price_arr += (t_price,)
                    #print ("Total RT array is :" + str (t_rsp_time_arr))
                    #print ("Task " + task.get_name () + \
                    #     " (" + str(task.is_offloadable ()) + ", " + task.get_type () + ") " + \
                    #     "is offloaded successfully on " + cand_n.get_n_id ())
                    # self._log.w ("RT: " + str (t_rsp_time) + ", EC: " + str (t_e_consum) + \
                    #     ", PR: " + str (t_price))
                    cand_n.terminate (task)
                    off_transactions.append ([cand_n.get_sc_id (), self.dynamic_t_incentive (cand_n, \
                        values, app_name)])

                    for site in off_sites:
                      site.reset_latencies ()

                    break
                
                # print ("############# OFFLOADING FAILURE on site " + cand_n.get_n_id () + " ##############################")
                # self._log.w ("Offloading failure occur on " + str (cand_n.get_node_type ()))
                (time_cost, e_cost, pr_cost) = Model.fail_cost (task, off_sites, cand_n, self._curr_n)
                #print ("Failure cost is RT: " + str (time_cost) + "s, EC: " + \
                #  str (e_cost) + "J, price: " + str (pr_cost) + " monetary units")
                t_fail_cost += time_cost
                e_fail_cost += e_cost
                pr_fail_cost += pr_cost
                # del metrics[cand_n]

                off_transactions.append ([cand_n.get_sc_id (), 0])
                self._off_fail_hist[cand_n.get_node_prototype ()] += 1
                # remove all offloading sites so mobile device can be selected as a candidate site for re-execution
                for site in off_sites:
                  if site.get_node_prototype () != NodePrototypes.MD:
                    del metrics[site]

            # print (self._curr_n.get_n_id () + " -> " + cand_n.get_n_id () + \
            #  " (task = " + task.get_name () + ", off = " + str (task.is_offloadable ()) + ")")
            self.__evaluate_constraint_violations (cand_n, t_rsp_time, app_name)

        (max_rsp_time, acc_e_consum, acc_price) = self.__get_total_objs (t_rsp_time_arr, \
            t_e_consum_arr, t_price_arr)
        self._BL = round (self._BL - acc_e_consum, 3)
        self._curr_n = cand_n

        # self._log.w  ('BATTERY LIFETIME: ' + str (self._BL))
        self._curr_app_time += round (max_rsp_time, 3)
        # print ("Total app RT: " + str (round (self._curr_app_time - max_rsp_time, 3)) +\
        #  " + " + str (round (max_rsp_time, 3)) + " = " + str (round (self._curr_app_time, 3)))
        self._rsp_time_hist.append (max_rsp_time)
        self._e_consum_hist.append (acc_e_consum)
        self._res_pr_hist.append (acc_price)

        return off_transactions


    def summarize (self, exe_cnt):

        self._stats.add_rsp_time (sum (self._rsp_time_hist))
        self._stats.add_e_consum (sum (self._e_consum_hist))
        self._stats.add_res_pr (sum (self._res_pr_hist))
        self._stats.add_bl (round (self._BL / Settings.BATTERY_LF * 100, 3))
        self._stats.add_qos_viol (round (self._qos_viol_cnt / exe_cnt * 100, 3))

        self._rsp_time_hist = list ()
        self._e_consum_hist = list ()
        self._res_pr_hist = list ()
        self._qos_viol_cnt = 0
        self._BL = Settings.BATTERY_LF


    def summarize_cell_stats (self, cell_name, avail_distros):
        # cell statistics
        self._cell_stats[cell_name].add_off_dist (self._off_dist_hist)
        self._cell_stats[cell_name].add_off_fail (self._off_fail_hist)
        self._cell_stats[cell_name].add_constr_viol (self._constr_viol_hist)
        # setting avail distros stats but not adding new stats as previous three cell statistical attributes
        self._cell_stats[cell_name].set_avail_distros (avail_distros)

        # reset failure, offloading distribution and constraint violation counters for next cell location
        self._off_dist_hist = dict ()
        self._off_fail_hist = dict ()
        self._constr_viol_hist = dict ()


    def log_stats (self):
        if self._disable_trace_log:
          return

        for key in self._cell_stats:
            self._log.w (self._cell_stats[key].get_all ())
        
        self._log.w (self._stats.get_all ())
        self._log.w (self._stats.get_cell_stats (self._cell_stats))


    def get_logger (self):

        return self._log


    def get_last_rsp_time (self):

        return self._rsp_time_hist[-1]


    def get_curr_node (self):

        return self._curr_n


    # when switching cells then current site of task execution has to be updated
    # current site of task execution has to be from current cell
    def set_curr_node (self, site):

        self._curr_n = site


    def __print_current_failures (self, off_sites, timestamp):

        cnt_fail_sites = 0

        # print ("####### CURRENT INFRASTRUCTURE FAILURES ######## ")
        for site in off_sites:
            if not site.avail_or_not (timestamp):
              # print (site.get_n_id () + " has a FAILURE!")
              cnt_fail_sites += 1

        # print ("Number of FAILED infrastructure sites: " + str (cnt_fail_sites) + " / " + str (len (off_sites)) + " = " + \
        #  str (round (cnt_fail_sites / len (off_sites), 2)))


    def __evaluate_constraint_violations (self, off_site, rt, app_name):

        constr = off_site.get_constr (app_name)

        if (constr.get_proc () + constr.get_lat ()) < rt:
            self._constr_viol_hist[off_site.get_node_prototype ()] += 1
            # print (off_site.get_n_id () + " has constraint violation " + \
            #    str (constr.get_proc () + constr.get_lat ()) + "s with response time " + \
            #    str (rt))

    
    def __check_off_sites (self, off_sites):

        for site in off_sites:
            if not site.get_node_prototype () in self._off_dist_hist.keys ():
                self._off_dist_hist[site.get_node_prototype ()] = 0
                self._off_fail_hist[site.get_node_prototype ()] = 0
                self._constr_viol_hist[site.get_node_prototype ()] = 0

            # site.eval_avail (timestamp)


    def __get_total_objs (self, rsp_arr, e_consum_arr, price_arr):

        max_rsp_time = 0
        for time in rsp_arr:
            if max_rsp_time < time:
                max_rsp_time = time

        acc_e_consum = 0
        for e_consum in e_consum_arr:
            acc_e_consum = acc_e_consum + e_consum

        acc_price = 0
        for price in price_arr:
           acc_price = acc_price + price

        max_rsp_time = round (max_rsp_time, 3)
        acc_e_consum = round (acc_e_consum, 3)
        acc_price = round (acc_price, 3)

        return (max_rsp_time, acc_e_consum, acc_price)


    def __compute_metrics (self, task, off_sites, curr_n):
        
        metrics = dict ()

        for cand_n in off_sites:
            (rsp_time, e_consum) = self.__compute_estimated_objectives (task, cand_n, curr_n)
            metrics[cand_n] = {'rt': rsp_time, 'ec': e_consum}

        for cand_n in off_sites:
            price = self.__compute_estimate_price (task, off_sites, cand_n, curr_n)
            metrics[cand_n]['pr'] = price
        
        # return self.__compute_score (metrics)
        return metrics


    def __compute_estimate_price (self, task, off_sites, cand_n, curr_n):
      
        return Model.price (task, off_sites, cand_n, curr_n)    

    
    # objectives are estimated per candidate offloading site
    def __compute_estimated_objectives (self, task, cand_n, curr_n):
        
        t_rsp_time = cand_n.est_lat (task, curr_n.get_n_id (), curr_n.get_node_prototype ())
        t_e_consum = Model.task_e_consum (t_rsp_time, cand_n, curr_n)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall ())


    def __runtime_objectives (self, task, off_sites, cand_n, curr_n):

        t_rsp_time = None
        t_e_consum = None
        t_price = 0.0
      
        for site in off_sites:
            if site == cand_n:
              t_rsp_time = site.act_lat (task, curr_n.get_n_id (), curr_n.get_node_prototype ())
              t_e_consum = Model.task_e_consum (t_rsp_time, site, curr_n)
              continue

            _ = site.act_lat (task, curr_n.get_n_id (), curr_n.get_node_prototype ())

        t_price = Model.price (task, off_sites, cand_n, curr_n)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall (), round (t_price, 3))


    @abstractmethod
    def offloading_decision(self, task, metrics):

        pass
