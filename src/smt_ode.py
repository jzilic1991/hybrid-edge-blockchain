from z3 import *
import random
import math
import time

from ode import OffloadingDecisionEngine
from task import Task
from util import NodeTypes, Settings, MobApps, NodePrototypes


class SmtOde (OffloadingDecisionEngine):

    def __init__(self, 
        name, 
        curr_n, 
        md, 
        app_name, 
        activate, 
        con_delay,
        alpha = None,
        beta = None,
        gamma = None,
        k = None,
        disable_trace_log = False):

        super().__init__(name, 
            curr_n, 
            md, 
            app_name, 
            con_delay,
            alpha = alpha,
            beta = beta,
            gamma = gamma,
            k = k,
            disable_trace_log = disable_trace_log)
        
        self._activate = activate
        self._disable_trace_log = disable_trace_log
        print(f"[SMT ODE INIT] α={self._alpha}, β={self._beta}, γ={self._gamma}, k={self._k}")


    def offloading_decision (self, task, metrics, timestamp, app_name, constr, qos, cell_name):

        if task.is_offloadable ():
            # self._k = round ((len (metrics) / 2))
            # print ("K param is " + str (self._k))
            (s, b_sites) = self.__smt_solving (task, self.__compute_score (metrics), timestamp, \
                app_name, constr, qos)
            
            # measuring offloading decision time
            start = time.time ()
            check = s.check ()
            end = time.time ()
            
            # storing overhead measurement
            if self._measure_off_dec_time:
              self._cell_stats[cell_name].add_overhead (len (metrics), round (end - start, 6))
              self._measure_off_dec_time = False

            # if solution has been found 
            if str(check) == 'sat':
                # self._log.w ("Time elapsed for SMT computing is " + str (round (end - start, 3)) + " s")
                sites_to_off = list ()
                # print (s.model ())

                for b in b_sites:
                    if is_true (s.model ()[b[0]]):
                        sites_to_off.append (b[1])

                return (sites_to_off[0], metrics[sites_to_off[0]])

            # if solution has not been found then best possible choice is selected by Rep-SMT
            if self._activate:
                site, metrics = self.__get_site_min_score (metrics, timestamp)
                return (site, metrics)

            # otherwise random site is picked by classical SMT solution 
            else:
                site = random.choice (list (metrics.items ()))
                return (site[0], metrics[site[0]])

            return (site, metric)
            # raise ValueError ("SMT solver did not find solution! s = " + str(s))

        for key, values in metrics.items ():
            if key.get_node_type() == NodeTypes.MOBILE:
                return (key, values)

        raise ValueError ("No mobile devices found!")


    def __smt_solving (self, task, metrics, timestamp, app_name, constr, qos):

        # metrics is a dict {OffloadingSite: dict {"rsp":, "e_consum":, "price": }}
        score = Real ('score')
        sites = [key for key, _ in metrics.items ()]
        b_sites = [(Bool (site.get_n_id ()), site) for site in sites]

        if self._activate:
            s = Optimize ()

        else:
            s = Solver ()

        # self.__print_smt_offload_info (metrics, b_sites, timestamp, app_name, qos)

        # append tuple (Bool, OffloadingSite) to list
        # b_sites.append ((Bool (site.get_n_id ()), site) for site in sites)
        # print ([metrics[b[1]]['score'] for b in b_sites])
        s.add (Or ([b[0] for b in b_sites]))
        s.add ([Implies (b[0] == True, \
                And (metrics[b[1]]['rt'] <= qos['rt'], \
                    metrics[b[1]]['rt'] <= (constr.get_proc () + constr.get_lat ()),\
                    metrics[b[1]]['ec'] <= task.get_ec (), \
                    # metrics[b[1]]['pr'] <= task.get_pr (), \
                    b[1].avail_or_not (timestamp) == True)) \
                    for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (Settings.BATTERY_LF >= (self._BL - metrics[b[1]]['ec']) \
                    / self._BL >= 0.0)) for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (b[1].get_mem_consum () < 1, \
                    b[1].get_stor_consum () < 1, \
                    metrics[b[1]]['score'] == score)) \
                    for b in b_sites])

        # adding reputation score in SMT formula
        if self._activate:
            
            rep_thr = self.__compute_rep_threshold (sites)
            # self._log.w ("Rep-SMT threshold is: " + str (rep_thr))

            s.add ([Implies (b[0] == True, \
                    And (b[1].get_reputation () >= rep_thr, \
                        1.0 >= b[1].get_reputation () >= 0.0)) \
                        for b in b_sites])

            s.minimize (score)

        return (s, b_sites)


    def __print_smt_offload_info (self, metrics, b_sites, timestamp, app_name, qos):
        if not disable_trace_log:
          self._log.w (app_name + " QoS: " + str (qos['rt']) + ' s')
        
        for triple in b_sites:
          if not disable_trace_log:
            self._log.w ("Name: " + triple[1].get_n_id ())
            self._log.w ("Available: " + str (triple[1].avail_or_not (timestamp)))
            self._log.w ("Processing latency constraint: " + str (triple[2].get_proc ()) + " s")
            self._log.w ("Network latency constraint: " + str (triple[2].get_lat ()) + " s")
            self._log.w ("Complete latency constraint: " + str (triple[2].get_proc () + \
                triple[2].get_lat ()) + " s")
            self._log.w ("Response time: " + str (metrics[triple[1]]['rt']) + " s")
            self._log.w ("Score: " + str (metrics[triple[1]]['score']))
            self._log.w ("")


    def __compute_local_optimum (self, metrics, obj):

        loc_opt = 0.0

        for site, val in metrics.items ():
            if loc_opt > metrics[site][obj]:
                loc_opt = metrics[site][obj]

        return loc_opt


    def __compute_score (self, metrics):

        rt = self.__compute_local_optimum (metrics, 'rt')
        ec = self.__compute_local_optimum (metrics, 'ec')
        pr = self.__compute_local_optimum (metrics, 'pr')
        
        for site, val in metrics.items ():
            metrics[site]['score'] = self._alpha * abs (val['rt'] - rt) + \
                self._beta * abs (val['ec'] - ec) + self._gamma * abs (val['pr'] - pr)
            # print ("Local optima RT: " + str (rt))
            # print ("Local optima EC: " + str (ec))
            # print ("Local optima PR: " + str (pr))
            # print ("Site " + str (site.get_n_id ()) + " has score " + str (metrics[site]['score']))
            # print ("RT value: " + str (val['rt']) + ", diff = " + str (Settings.W_RT * (val['rt'] - rt)))
            # print ("EC value: " + str (val['ec']) + ", diff = " + str (Settings.W_EC * (val['ec'] - ec)))
            # print ("PR value: " + str (val['pr']) + ", diff = " + str (Settings.W_PR * (val['pr'] - pr)))
            # print ("")

            if metrics[site]['score'] == math.inf:
                metrics[site]['score'] = 100

        return metrics


    def __compute_rep_threshold (self, off_sites):

        reps = [site.get_reputation () for site in off_sites]
        return min (sorted (reps, key = lambda x: x, reverse = True)[:self._k])


    def __get_site_min_score (self, metrics, timestamp):

        min_score = math.inf
        site = None
        
        for key, value in metrics.items ():
            
            if value['score'] < min_score and key.avail_or_not (timestamp):
                min_score = value['score']
                site = key

        # self._log.w ("Min score of " + str (min_score) + " has site " + site.get_n_id ())

        return (site, metrics[site])
