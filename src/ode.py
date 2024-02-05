import math
from abc import ABC, abstractmethod

from util import Settings, NodePrototypes, ResponseTime
from stats import Stats
from cell_stats import CellStats
from logger import Logger
from models import Model


class OffloadingDecisionEngine(ABC):

    def __init__(self, name, curr_n, md, app_name, con_delay, scala):
            
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
        self._log = Logger ('logs/sim_traces_' + self._name + '_' + app_name + '.txt', True, 'w')

        super().__init__()


    def get_name(cls):
        
        return cls._name


    def get_current_site (cls):

        return cls._curr_n


    def get_md (cls):

        return cls._md


    def dynamic_t_incentive (cls, site, metric, app_name):

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


    def set_cell_stats (cls, cell_name):

        if not cell_name in cls._cell_stats:

            cls._cell_stats[cell_name] = CellStats (cell_name)


    def app_exc_done (cls, qos):

        if qos['rt'] < cls._curr_app_time:

            # cls._log.w ("QoS is violated! RT: " + str (cls._curr_app_time) + "s, QoS: " + \
            #     str (qos['rt']) + "s")
            cls._qos_viol_cnt += 1

        cls._curr_app_time = 0.0


    def offload (cls, tasks, off_sites, topology, timestamp, app_name, qos, \
      task_off_queue, task_del_queue):

        if cls._BL <= 0.0:

            return []

        cand_n = None
        t_rsp_time_arr = tuple ()
        t_e_consum_arr = tuple ()
        t_price_arr = tuple ()
        off_transactions = list ()

        # check does offloading site history statistics exists
        cls.__check_off_sites (off_sites)

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

            metrics = cls.__compute_metrics (task, off_sites, \
                cls._curr_n, topology, task_off_queue, task_del_queue)

            while True:

                cand_n, values = cls.offloading_decision (task, metrics, timestamp, app_name, \
                    constr, qos)

                cls._off_dist_hist[cand_n.get_n_id ()] = \
                    cls._off_dist_hist[cand_n.get_n_id ()] + 1

                if cand_n.execute (task, timestamp):

                    # t_rsp_time = t_rsp_time + values['rt']
                    # t_e_consum = t_e_consum + values['ec']
                    # t_price = t_price + values['pr']
                    (t_rsp_time, t_e_consum, t_price) = cls.__runtime_objectives (task, off_sites, \
                      cand_n, cls._curr_n, topology, task_off_queue, task_del_queue)
                    t_rsp_time_arr += (t_rsp_time,)
                    t_e_consum_arr += (t_e_consum,)
                    t_price_arr += (t_price,)
                    # cls._log.w ("Task " + task.get_name () + \
                    #      " (" + str(task.is_offloadable ()) + ", " + task.get_type () + ") " + \
                    #      "is offloaded successfully on " + cand_n.get_n_id ())
                    # cls._log.w ("RT: " + str (t_rsp_time) + ", EC: " + str (t_e_consum) + \
                    #     ", PR: " + str (t_price))
                    cand_n.terminate (task)
                    off_transactions.append ([cand_n.get_sc_id (), cls.dynamic_t_incentive (cand_n, \
                        values, app_name)])
                    break

                else:

                    # cls._log.w ("OFFLOADING FAILURE on site " + cand_n.get_n_id ())
                    # cls._log.w ("Offloading failure occur on " + str (cand_n.get_node_type ()))
                    (time_cost, e_cost) = Model.fail_cost (cand_n, cls._curr_n)
                    # cls._log.w ("Failure cost is RT:" + str (time_cost) + "s, EC: " + \
                    #     str (e_cost) + " J")
                    t_rsp_time = t_rsp_time + time_cost
                    t_e_consum = t_e_consum + e_cost
                    del metrics[cand_n]
                    off_transactions.append ([cand_n.get_sc_id (), 0])
                    cls._off_fail_hist[cand_n.get_n_id ()] = \
                        cls._off_fail_hist[cand_n.get_n_id ()] + 1
                    continue

            cls.__evaluate_constraint_violations (cand_n, t_rsp_time, app_name)

        (max_rsp_time, acc_e_consum, acc_price) = cls.__get_total_objs (t_rsp_time_arr, \
            t_e_consum_arr, t_price_arr)
        cls._BL = round (cls._BL - acc_e_consum, 3)
        cls._curr_n = cand_n

        # cls._log.w  ('BATTERY LIFETIME: ' + str (cls._BL))
        cls._curr_app_time += max_rsp_time
        cls._rsp_time_hist.append (max_rsp_time)
        cls._e_consum_hist.append (acc_e_consum)
        cls._res_pr_hist.append (acc_price)

        return off_transactions


    def summarize (cls):

        cls._stats.add_rsp_time (sum (cls._rsp_time_hist))
        cls._stats.add_e_consum (sum (cls._e_consum_hist))
        cls._stats.add_res_pr (sum (cls._res_pr_hist))
        cls._stats.add_bl (round (cls._BL / Settings.BATTERY_LF * 100, 3))
        cls._stats.add_qos_viol (cls._qos_viol_cnt)

        cls._rsp_time_hist = list ()
        cls._e_consum_hist = list ()
        cls._res_pr_hist = list ()
        cls._qos_viol_cnt = 0
        cls._BL = Settings.BATTERY_LF


    def summarize_cell_stats (cls, cell_name):

        # cell statistics
        cls._cell_stats[cell_name].add_off_dist (cls._off_dist_hist)
        cls._cell_stats[cell_name].add_off_fail (cls._off_fail_hist)
        cls._cell_stats[cell_name].add_constr_viol (cls._constr_viol_hist)

        # reset failure and offloading distribution counters for next cell location
        cls._off_dist_hist = dict ()
        cls._off_fail_hist = dict ()
        cls._constr_viol_hist = dict ()


    def log_stats (cls):

        for key in cls._cell_stats:

            cls._log.w (cls._cell_stats[key].get_all ())
        
        cls._log.w (cls._stats.get_all ())
        cls._log.w (cls._stats.get_cell_stats (cls._cell_stats))


    def get_logger (cls):

        return cls._log


    def __evaluate_constraint_violations (cls, off_site, rt, app_name):

        constr = off_site.get_constr (app_name)

        if (constr.get_proc () + constr.get_lat ()) < rt:

            cls._constr_viol_hist[off_site.get_n_id ()] += 1
            # cls._log.w (off_site.get_n_id () + " has constraint violation " + \
            #     str (constr.get_proc () + constr.get_lat ()) + "s with response time " + \
            #     str (rt))

    
    def __check_off_sites (cls, off_sites):

        for site in off_sites:

            if not site.get_n_id () in cls._off_dist_hist.keys ():

                cls._off_dist_hist[site.get_n_id ()] = 0
                cls._off_fail_hist[site.get_n_id ()] = 0
                cls._constr_viol_hist[site.get_n_id ()] = 0

            # site.eval_avail (timestamp)


    def __get_total_objs (cls, rsp_arr, e_consum_arr, price_arr):

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


    def __compute_metrics (cls, task, off_sites, curr_n, topology, task_off_queue, \
      task_del_queue):
        
        metrics = dict ()

        # estimations for offloading and delivery queueing latencies are the 
        # same because they are based on average rates which does not change
        off_est_lat = task_off_queue.est_lat (off_sites, task)
        del_est_lat = task_del_queue.est_lat (off_sites, task)
        print ("Estimated offloading latency is " + str (off_est_lat))
        print ("Estimated delivery latency is " + str (del_est_lat))

        for cand_n in off_sites:
               
            (rsp_time, e_consum, price) = cls.__compute_estimated_objectives (task, off_sites, cand_n, \
                curr_n, topology, off_est_lat, del_est_lat)
            metrics[cand_n] = {'rt': rsp_time, 'ec': e_consum, 'pr': price}

        # return cls.__compute_score (metrics)
        return metrics

    # objectives are estimated per candidate offloading site
    def __compute_estimated_objectives (cls, task, off_sites, cand_n, curr_n, topology, \
      off_est_lat, del_est_lat):
        
        exe_est_lat = cand_n.est_lat (task)
        total_est_lat = off_est_lat + exe_est_lat + del_est_lat
        
        print ("Estimated execution latency (" + cand_n.get_node_type () + ") is " + str (exe_est_lat))
        print ("Estimated total latency is " + str (total_est_lat))
        
        t_rsp_time = ResponseTime (exe_est_lat, del_est_lat, off_est_lat, total_est_lat)
        t_e_consum = Model.task_e_consum (t_rsp_time, cand_n, curr_n)
        t_price = Model.price (task, off_sites, cand_n, curr_n, topology)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall (), \
            round (t_price, 3))


    def __runtime_objectives (cls, task, off_sites, cand_n, curr_n, topology, \
      task_off_queue, task_del_queue):

        off_act_lat = task_off_queue.act_lat (off_sites, task)
        exe_act_lat = cand_n.act_lat (task)
        del_act_lat = task_del_queue.act_lat (off_sites, task)
        total_act_lat = off_act_lat + exe_act_lat + del_act_lat
        
        print ("Actual offloading latency is " + str (off_act_lat))
        print ("Actual delivery latency is " + str (del_act_lat))
        print ("Actual execution latency (" + cand_n.get_node_type () + ") is " + str (exe_act_lat))
        print ("Actual total latency is " + str (total_act_lat))

        t_rsp_time = ResponseTime (exe_act_lat, del_act_lat, off_act_lat, total_act_lat)
        t_e_consum = Model.task_e_consum (t_rsp_time, cand_n, curr_n)
        t_price = Model.price (task, off_sites, cand_n, curr_n, topology)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall (), \
            round (t_price, 3))



    @abstractmethod
    def offloading_decision(cls, task, metrics):

        pass
