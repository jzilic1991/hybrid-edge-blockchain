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


    def dynamic_t_incentive (cls, task, metric):

        tmp = round ((task.get_rt () - metric['rt']) / task.get_rt (), 3) * 1000

        if tmp == math.inf or tmp == -math.inf:

            incentive = 0

        else:

            incentive = int (tmp)
        
        if incentive >= 0 and incentive <= 1000:

            return incentive

        return 0


    def offloading_decision(cls, task, metrics, app_name, qos):
        
        if task.is_offloadable ():

            (s, b_sites) = cls.__smt_solving (task, cls.__compute_score (metrics), app_name, qos)
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

            return random.choice (list (metrics.items ()))
            # raise ValueError ("SMT solver did not find solution! s = " + str(s))

        for key, values in metrics.items ():
                
            if key.get_node_type() == NodeTypes.MOBILE:
                    
                return (key, values)

        raise ValueError ("No mobile devices found!")


    def __smt_solving (cls, task, metrics, app_name, qos):

        # metrics is a dict {OffloadingSite: dict {"rsp":, "e_consum":, "price": }}
        score = Real ('score')
        sites = [key for key, _ in metrics.items ()]
        b_sites = [(Bool (site.get_n_id ()), site) for site in sites]
        s = Optimize ()

        # append tuple (Bool, OffloadingSite) to list
        # b_sites.append ((Bool (site.get_n_id ()), site) for site in sites)
        # print ([metrics[b[1]]['score'] for b in b_sites])

        s.add (Or ([b[0] for b in b_sites]))
        s.add ([Implies (b[0] == True, \
                And (metrics[b[1]]['rt'] <= qos['rt'], \
                    b[1].get_constraints(),
                    metrics[b[1]]['ec'] <= task.get_ec (), \
                    metrics[b[1]]['pr'] <= task.get_pr (), \
                    metrics[b[1]]['score'] == score)) \
                    for b in b_sites])        
        s.add ([Implies (b[0] == True, \
                And (Settings.BATTERY_LF >= (cls._BL - metrics[b[1]]['ec']) \
                    / cls._BL >= 0.0)) for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (b[1].get_mem_consum () < 1, \
                    b[1].get_stor_consum () < 1)) \
                    for b in b_sites])

        if cls._activate:
            
            rep_thr = cls.__compute_rep_threshold (sites)
            cls._log.w ("Rep-SMT threshold is: " + str (rep_thr))

            s.add ([Implies (b[0] == True, \
                    And (b[1].get_reputation () >= rep_thr, \
                        1.0 >= b[1].get_reputation () >= 0.0)) \
                        for b in b_sites])

        s.minimize (score)

        return (s, b_sites)


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