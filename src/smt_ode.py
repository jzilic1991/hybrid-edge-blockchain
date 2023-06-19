from z3 import *
import random
import math
import time

from ode import OffloadingDecisionEngine
from task import Task
from util import NodeTypes, Settings, MobApps


class SmtOde (OffloadingDecisionEngine):


    def __init__(self, name, curr_n, md, app_name, activate, con_delay, scala):

        super().__init__(name, curr_n, md, app_name, con_delay, scala)
        self._activate = activate
        self._k = 3


    def offloading_decision(cls, task, metrics, timestamp, app_name, qos):

        if task.is_offloadable ():

            (s, b_sites) = cls.__smt_solving (task, cls.__compute_score (metrics), timestamp, \
                app_name, qos)
            start = time.time ()

            if str(s.check ()) == 'sat':

                end = time.time ()
                # cls._log.w ("Time elapsed for SMT computing is " + str (round (end - start, 3)) + " s")
                sites_to_off = list ()

                # print (s.model ())

                for b in b_sites:

                    if is_true (s.model ()[b[0]]):

                        sites_to_off.append (b[1])

                return (sites_to_off[0], metrics[sites_to_off[0]])

            #site = random.choice (list (metrics.items ()))
            site, metric = cls.__get_site_min_score (metrics, timestamp)
            return (site, metric)
            # raise ValueError ("SMT solver did not find solution! s = " + str(s))

        for key, values in metrics.items ():

            if key.get_node_type() == NodeTypes.MOBILE:

                return (key, values)

        raise ValueError ("No mobile devices found!")


    def __smt_solving (cls, task, metrics, timestamp, app_name, qos):

        # metrics is a dict {OffloadingSite: dict {"rsp":, "e_consum":, "price": }}
        score = Real ('score')
        sites = [key for key, _ in metrics.items ()]
        b_sites = [(Bool (site.get_n_id ()), site, site.get_constr (app_name)) \
            for site in sites]
        s = Optimize ()

        cls.__print_smt_offload_info (metrics, b_sites, timestamp, app_name, qos)

        # append tuple (Bool, OffloadingSite) to list
        # b_sites.append ((Bool (site.get_n_id ()), site) for site in sites)
        # print ([metrics[b[1]]['score'] for b in b_sites])

        s.add (Or ([b[0] for b in b_sites]))
        s.add ([Implies (b[0] == True, \
                And (metrics[b[1]]['rt'] <= qos['rt'], \
                    metrics[b[1]]['rt'] <= (b[2].get_proc () + b[2].get_lat ()),\
                    metrics[b[1]]['ec'] <= task.get_ec (), \
                    metrics[b[1]]['pr'] <= task.get_pr (), \
                    metrics[b[1]]['score'] == score, \
                    b[1].avail_or_not (timestamp) == True)) \
                    for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (Settings.BATTERY_LF >= (cls._BL - metrics[b[1]]['ec']) \
                    / cls._BL >= 0.0)) for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (b[1].get_mem_consum () < 1, \
                    b[1].get_stor_consum () < 1)) \
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

        cls._log.w ("Min score of " + str (min_score) + " has site " + site.get_n_id ())

        return (site, metrics[site])