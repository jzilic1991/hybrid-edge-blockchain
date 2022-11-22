from z3 import *
import random
import math

from ode import OffloadingDecisionEngine
from task import Task
from util import NodeTypes, Settings


class SmtOde (OffloadingDecisionEngine):

    def __init__(self, name, curr_n, md, activate):

        super().__init__(name, curr_n, md)
        self._activate = activate


    def dynamic_t_incentive (cls, task, metric):

        incentive = int (round ((task.get_rt () - metric['rt']) / task.get_rt (), 3) * 1000)
        # int(round(random.uniform (0, 1), 3) * 1000)
        # cls._log.w ("Task incentive is " + str (incentive))

        if incentive >= 0 and incentive <= 1000:

            return incentive

        return 0


    def offloading_decision(cls, task, metrics):
        
        if task.is_offloadable ():

            (s, b_sites) = cls.__smt_solving (task, cls.__compute_score (metrics))
            
            if str(s.check ()) == 'sat':
                
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


    def __smt_solving (cls, task, metrics):

        # metrics is a dict {OffloadingSite: dict {"rsp":, "e_consum"}}
        score = Real ('score')
        sites = [key for key, _ in metrics.items ()]
        b_sites = [(Bool (site.get_n_id ()), site) for site in sites]
        s = Optimize ()

        # append tuple (Bool, OffloadingSite) to list
        # b_sites.append ((Bool (site.get_n_id ()), site) for site in sites)

        s.add (Or ([b[0] for b in b_sites]))
        s.add ([Implies (b[0] == True, \
                And (metrics[b[1]]['rt'] <= task.get_rt (), \
                    metrics[b[1]]['ec'] <= task.get_ec (), \
                    metrics[b[1]]['pr'] <= task.get_pr (),
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
            
            s.add ([Implies (b[0] == True, \
                    And (b[1].get_reputation () >= cls._REP, \
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

        return metrics