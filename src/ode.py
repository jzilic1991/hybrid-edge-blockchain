from abc import ABC, abstractmethod

from util import Settings
from stats import Stats
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
        self._qos_viol_hist = 0
        self._obj_viol_hist = {'rt': 0, 'ec': 0, 'pr': 0}
        self._stats = Stats ()

        if scala > 0:

            self._log = Logger ('logs/scala_' + str(scala) + '.txt', True, 'w')

        else:

            self._log = Logger ('logs/sim_traces_' + self._name + '_' + app_name + '_' + str(con_delay) + \
                '.txt', True, 'w')

        super().__init__()


    def get_name(cls):
        
        return cls._name


    def get_current_site (cls):

        return cls._curr_n


    def get_md (cls):

        return cls._md


    def offload (cls, tasks, off_sites, topology, timestamp):

        if cls._BL <= 0.0:

            return []

        cand_n = None
        t_rsp_time_arr = tuple ()
        t_e_consum_arr = tuple ()
        t_price_arr = tuple ()
        off_transactions = list ()

        cls.__check_off_sites (off_sites, timestamp)
    
        for task in tasks:

            t_rsp_time = 0.0
            t_e_consum = 0.0
            t_price = 0.0

            metrics = cls.__compute_metrics (task, off_sites, \
                cls._curr_n, topology)

            while True:

                cand_n, values = cls.offloading_decision (task, metrics)

                cls._off_dist_hist[cand_n.get_n_id ()] = \
                    cls._off_dist_hist[cand_n.get_n_id ()] + 1

                if cand_n.execute (task, timestamp):

                    t_rsp_time = t_rsp_time + values['rt']
                    t_e_consum = t_e_consum + values['ec']
                    t_price = t_price + values['pr']
                    t_rsp_time_arr += (t_rsp_time,)
                    t_e_consum_arr += (t_e_consum,)
                    t_price_arr += (t_price,)
                    # cls._log.w ("Task " + task.get_name () + \
                    #     " (" + str(task.is_offloadable ()) + ", " + task.get_type () + ") " + \
                    #     "is offloaded successfully on " + cand_n.get_n_id ())
                    # cls._log.w ("RT: " + str (t_rsp_time) + ", EC: " + str (t_e_consum) + \
                    #     ", PR: " + str (t_price))
                    cls.__determine_qos_violations (task, metrics[cand_n])
                    cand_n.terminate (task)
                    off_transactions.append ([cand_n.get_sc_id (), cls.dynamic_t_incentive (task, \
                        metrics[cand_n])])
                    break

                else:

                    # cls._log.w ("OFFLOADING FAILURE on site " + cand_n.get_n_id ())
                    # print ("Offloading failure occur on " + str (cand_n))
                    (time_cost, e_cost) = Model.fail_cost (cand_n, cls._curr_n)
                    # cls._log.w ("Failure cost is RT:" + str (time_cost) + "s, EC: " + \
                    #     str (e_cost) + " J")
                    t_rsp_time = t_rsp_time + time_cost
                    t_e_consum = t_e_consum + e_cost
                    cls._qos_viol_hist = cls._qos_viol_hist + 1
                    del metrics[cand_n]
                    off_transactions.append ([cand_n.get_sc_id (), 0])
                    cls._off_fail_hist[cand_n.get_n_id ()] = \
                        cls._off_fail_hist[cand_n.get_n_id ()] + 1

        (max_rsp_time, acc_e_consum, acc_price) = cls.__get_total_objs (t_rsp_time_arr, \
            t_e_consum_arr, t_price_arr)
        cls._BL = round (cls._BL - acc_e_consum, 3)
        cls._curr_n = cand_n

        # cls._log.w  ('BATTERY LIFETIME: ' + str (cls._BL))
        cls._rsp_time_hist.append (max_rsp_time)
        cls._e_consum_hist.append (acc_e_consum)
        cls._res_pr_hist.append (acc_price)

        return off_transactions
    

    def summarize (cls):

        cls._stats.add_rsp_time (sum (cls._rsp_time_hist))
        cls._stats.add_e_consum (sum (cls._e_consum_hist))
        cls._stats.add_res_pr (sum (cls._res_pr_hist))
        cls._stats.add_bl (round (cls._BL / Settings.BATTERY_LF * 100, 3))
        cls._stats.add_off_dist (cls._off_dist_hist)
        cls._stats.add_off_fail (cls._off_fail_hist)
        cls._stats.add_qos_viol (cls._qos_viol_hist)
        cls._stats.add_obj_viol (cls._obj_viol_hist)

        cls._rsp_time_hist = list ()
        cls._e_consum_hist = list ()
        cls._res_pr_hist = list ()
        cls._off_dist_hist = dict ()
        cls._off_fail_hist = dict ()
        cls._qos_viol_hist = 0
        cls._obj_viol_hist = {'rt': 0, 'ec': 0, 'pr': 0}
        cls._BL = Settings.BATTERY_LF


    def log_stats (cls):

        cls._log.w (cls._stats.get_all ())


    def get_logger (cls):

        return cls._log


    def __determine_qos_violations (cls, task, metric):

        qos_viol_flag = False

        if task.get_rt () <= metric['rt']:

            cls._obj_viol_hist['rt'] = cls._obj_viol_hist['rt'] + 1
            qos_viol_flag = True

        if task.get_ec () <= metric['ec']:

            cls._obj_viol_hist['ec'] = cls._obj_viol_hist['ec'] + 1
            qos_viol_flag = True

        if task.get_pr () <= metric['pr']:

            cls._obj_viol_hist['pr'] = cls._obj_viol_hist['pr'] + 1
            qos_viol_flag = True

        if qos_viol_flag:

            cls._qos_viol_hist = cls._qos_viol_hist + 1


    def __check_off_sites (cls, off_sites, timestamp):

        for site in off_sites:

            if not site.get_n_id () in cls._off_dist_hist.keys ():

                cls._off_dist_hist[site.get_n_id ()] = 0
                cls._off_fail_hist[site.get_n_id ()] = 0

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


    def __compute_metrics (cls, task, off_sites, curr_n, topology):
        
        metrics = dict ()

        for cand_n in off_sites:
            
            (rsp_time, e_consum, price) = cls.__compute_objectives (task, off_sites, cand_n, \
                curr_n, topology)
            metrics[cand_n] = {'rt': rsp_time, 'ec': e_consum, 'pr': price}

        # return cls.__compute_score (metrics)
        return metrics


    def __compute_objectives (cls, task, off_sites, cand_n, curr_n, topology):
        
        t_rsp_time = Model.task_rsp_time (task, cand_n, curr_n, topology)
        t_e_consum = Model.task_e_consum (t_rsp_time, cand_n, curr_n)
        t_price = Model.price (task, off_sites, cand_n, curr_n, topology)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall (), \
            round (t_price, 3))


    @abstractmethod
    def dynamic_t_incentive (cls, task, metric):

        pass


    @abstractmethod
    def offloading_decision(cls, task, metrics):

        pass