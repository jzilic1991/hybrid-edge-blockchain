from z3 import *
import random

from ode import OffloadingDecisionEngine
from models import Model
from task import Task
from util import NodeTypes, Settings


class SmtOde(OffloadingDecisionEngine):

    def __init__(self, name, curr_n, md):

        super().__init__(name, curr_n, md)
        self._REP = random.uniform (0, 1)
        self._BL = Settings.BATTERY_LF


    def offload(cls, tasks, off_sites, topology):

        cand_n = None
        t_rsp_time_arr = tuple ()
        t_e_consum_arr = tuple ()
    
        for task in tasks:

            t_rsp_time = 0
            t_e_consum = 0

            while True:

                metrics = cls.__compute_metrics (task, cls._curr_n, \
                    off_sites, topology)
                cand_n, values = cls.__offloading_decision (task, metrics)

                t_rsp_time = round (t_rsp_time + values['rt'], 3)
                t_e_consum = round (t_e_consum + values['ec'], 3)

                if cand_n.execute (task):

                    t_rsp_time_arr += (t_rsp_time,)
                    t_e_consum_arr += (t_e_consum,)
                    print ("Task " + task.get_name () + \
                        " (" + str(task.is_offloadable ()) + ") " + \
                        "is offloaded on " + cand_n.get_n_id ())
                    print ("RT: " + str(t_rsp_time) + ", EC: " + str(t_e_consum))
                    cand_n.terminate (task)
                    break

        (max_rsp_time, acc_e_consum) = cls.__get_rsp_and_e_consum (t_rsp_time_arr, \
            t_e_consum_arr)

        cls._curr_n = cand_n

        return (round (max_rsp_time, 3), round (acc_e_consum, 3))


    def __get_rsp_and_e_consum (cls, rsp_arr, e_consum_arr):

        max_rsp_time = 0
        for time in rsp_arr:
            if max_rsp_time < time:
                max_rsp_time = time

        acc_e_consum = 0
        for e_consum in e_consum_arr:
            acc_e_consum = acc_e_consum + e_consum

        return (max_rsp_time, acc_e_consum)


    def __offloading_decision(cls, task, metrics):
        
        if task.is_offloadable ():

            (s, b_sites) = cls.__cr_smt_solver (task, metrics)
            
            if str(s.check ()) == 'sat':
                
                sites_to_off = list ()

                print (s.model ())
                
                for b in b_sites:
                    
                    if is_true (s.model ()[b[0]]):

                        sites_to_off.append (b[1])
                
                return (sites_to_off[0], metrics[sites_to_off[0]])

            raise ValueError ("SMT solver did not find solution! s = " + str(s))

        for key, values in metrics.items ():
                
            if key.get_node_type() == NodeTypes.MOBILE:
                    
                return (key, values)

        raise ValueError ("No mobile devices found!")


    def __cr_smt_solver (cls, task, metrics):

        # metrics is a dict {OffloadingSite: dict {"rsp":, "e_consum"}}
        rsp = Real ('rsp')
        sites = [key for key, _ in metrics.items ()]
        b_sites = list ()
        s = Optimize ()

        for site in sites:

            # append tuple (Bool, OffloadingSite) to list
            b_sites.append ((Bool (site.get_n_id ()), site))

        s.add (Or ([b[0] for b in b_sites]))
        s.add ([Implies (b[0] == True, \
                And (metrics[b[1]]['rt'] <= task.get_rt (), \
                    metrics[b[1]]['ec'] <= task.get_ec (),
                    metrics[b[1]]['rt'] == rsp)) \
                    for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (b[1].get_reputation () >= cls._REP, \
                    1.0 >= b[1].get_reputation () >= 0.0)) \
                    for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (Settings.BATTERY_LF >= (cls._BL - metrics[b[1]]['ec']) \
                    / cls._BL >= 0.0)) for b in b_sites])
        s.add ([Implies (b[0] == True, \
                And (b[1].get_mem_consum () < 1, \
                    b[1].get_stor_consum () < 1)) \
                    for b in b_sites])

        s.minimize (rsp)

        return (s, b_sites)


    def __compute_metrics (cls, task, curr_n, off_sites, topology):
        
        metrics = dict ()

        for cand_n in off_sites:
            (rsp_time, e_consum) = cls.__compute_objectives (task, cand_n, curr_n,\
                topology)
            metrics[cand_n] = {'rt': rsp_time, 'ec': e_consum}

        return metrics


    def __compute_objectives (cls, task, cand_n, curr_n, topology):
        
        t_rsp_time = Model.task_rsp_time (task, cand_n, curr_n, topology)
        t_e_consum = Model.task_e_consum (t_rsp_time, cand_n, curr_n)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall ())