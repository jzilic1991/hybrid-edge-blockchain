from z3 import *
import random
import math
import time

from ode import OffloadingDecisionEngine
from task import Task
from util import NodeTypes, Settings, MobApps, NodePrototypes


class SmtOde (OffloadingDecisionEngine):


    def __init__(self, name, curr_n, md, app_name, activate, con_delay):

        super().__init__(name, curr_n, md, app_name, con_delay)
        self._activate = activate
        self._k = Settings.K


    def offloading_decision (cls, task, metrics, timestamp, app_name, constr, qos, cell_name):

        if task.is_offloadable ():
            # cls._k = round ((len (metrics) / 2))
            # print ("K param is " + str (cls._k))
            (s, b_sites) = cls.__smt_solving (task, cls.__compute_score (metrics), timestamp, \
                app_name, constr, qos)
            
            # measuring offloading decision time
            start = time.time ()
            check = s.check ()
            end = time.time ()
            
            # storing overhead measurement
            if cls._measure_off_dec_time:
              cls._cell_stats[cell_name].add_overhead (len (metrics), round (end - start, 6))
              cls._measure_off_dec_time = False

            # if solution has been found 
            if str(check) == 'sat':
                # cls._log.w ("Time elapsed for SMT computing is " + str (round (end - start, 3)) + " s")
                sites_to_off = list ()
                # print (s.model ())

                for b in b_sites:
                    if is_true (s.model ()[b[0]]):
                        sites_to_off.append (b[1])

                return (sites_to_off[0], metrics[sites_to_off[0]])

            # if solution has not been found then best possible choice is selected by Rep-SMT
            if cls._activate:
                site, metrics = cls.__get_site_min_score (metrics, timestamp)
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


    def __smt_solving (cls, task, metrics, timestamp, app_name, constr, qos):

        # metrics is a dict {OffloadingSite: dict {"rsp":, "e_consum":, "price": }}
        score = Real ('score')
        sites = [key for key, _ in metrics.items ()]
        b_sites = [(Bool (site.get_n_id ()), site) for site in sites]

        if cls._activate:
            s = Optimize ()

        else:
            s = Solver ()

        # cls.__print_smt_offload_info (metrics, b_sites, timestamp, app_name, qos)

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
                And (Settings.BATTERY_LF >= (cls._BL - metrics[b[1]]['ec']) \
                    / cls._BL >= 0.0)) for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (b[1].get_mem_consum () < 1, \
                    b[1].get_stor_consum () < 1, \
                    metrics[b[1]]['score'] == score)) \
                    for b in b_sites])

        # adding reputation score in SMT formula
        if cls._activate:
            
            rep_thr = cls.__compute_rep_threshold (sites)
            # cls._log.w ("Rep-SMT threshold is: " + str (rep_thr))

            s.add ([Implies (b[0] == True, \
                    And (b[1].get_reputation () >= rep_thr, \
                        1.0 >= b[1].get_reputation () >= 0.0)) \
                        for b in b_sites])

            s.minimize (score)

        return (s, b_sites)


    def __print_smt_offload_info (cls, metrics, b_sites, timestamp, app_name, qos):

        cls._log.w (app_name + " QoS: " + str (qos['rt']) + ' s')
        
        for triple in b_sites:

            cls._log.w ("Name: " + triple[1].get_n_id ())
            cls._log.w ("Available: " + str (triple[1].avail_or_not (timestamp)))
            cls._log.w ("Processing latency constraint: " + str (triple[2].get_proc ()) + " s")
            cls._log.w ("Network latency constraint: " + str (triple[2].get_lat ()) + " s")
            cls._log.w ("Complete latency constraint: " + str (triple[2].get_proc () + \
                triple[2].get_lat ()) + " s")
            cls._log.w ("Response time: " + str (metrics[triple[1]]['rt']) + " s")
            cls._log.w ("Score: " + str (metrics[triple[1]]['score']))
            cls._log.w ("")


    def __compute_local_optimum (cls, metrics, obj):

        loc_opt = 0.0

        for site, val in metrics.items ():
            if loc_opt > metrics[site][obj]:
                loc_opt = metrics[site][obj]

        return loc_opt


    def __compute_score (cls, metrics):

        rt = cls.__compute_local_optimum (metrics, 'rt')
        ec = cls.__compute_local_optimum (metrics, 'ec')
        pr = cls.__compute_local_optimum (metrics, 'pr')
        
        for site, val in metrics.items ():
            metrics[site]['score'] = Settings.W_RT * abs (val['rt'] - rt) + \
                Settings.W_EC * abs (val['ec'] - ec) + Settings.W_PR * abs (val['pr'] - pr)
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


    def __compute_rep_threshold (cls, off_sites):

        reps = [site.get_reputation () for site in off_sites]
        return min (sorted (reps, key = lambda x: x, reverse = True)[:cls._k])


    def __get_site_min_score (cls, metrics, timestamp):

        min_score = math.inf
        site = None
        
        for key, value in metrics.items ():
            
            if value['score'] < min_score and key.avail_or_not (timestamp):
                min_score = value['score']
                site = key

        # cls._log.w ("Min score of " + str (min_score) + " has site " + site.get_n_id ())

        return (site, metrics[site])
