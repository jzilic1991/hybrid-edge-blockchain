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

                t_rsp_time = t_rsp_time + values['rsp']
                t_e_consum = t_e_consum + values['e_consum']

                if cand_n.execute (task):

                    t_rsp_time_arr += (t_rsp_time,)
                    t_e_consum_arr += (t_e_consum,)
                    cand_n.terminate (task)
                    break

        max_rsp_time = 0
        for time in t_rsp_time_arr:
            if max_rsp_time < time:
                max_rsp_time = time

        acc_e_consum = 0
        for e_consum in t_e_consum_arr:
            acc_e_consum = acc_e_consum + e_consum

        cls._curr_n = cand_n

        return (round (max_rsp_time, 3), round (acc_e_consum, 3))


    def __offloading_decision(cls, task, metrics):
        
        if task.is_offloadable ():

            s = cls.__cr_smt_solver (metrics)
            
            if str(s.check ()) == 'sat':
                
                 = s.model ()
                key = list (ele.keys ())[0]
                values = list (ele.values ())[0]

                return (key, values)

            else:

                raise ValueError ("SMT solver did not find solution!")

        else:

            for ele in metrics:

                key = list (ele.keys ())[0]
                values = list (ele.values ())[0]
                
                if key.get_node_type() == NodeTypes.MOBILE:
                    
                    return (key, values)


    def __cr_smt_solver (cls, metrics)
        
        sites = [key in metrics.keys ()]
        s = Solver ()

        s.add (Or ([Bool (site.get_name ()) for site in sites]))
        s.add ([Implies (Bool (site.get_name ()) == True, \
                And (metrics[site]['rt'] <= task.get_rt (), \
                    metrics[site]['ec'] <= tasl.get_ec ())) \
                    for site in sites])
        s.add ([Implies (Bool (site.get_name ()) == True, \
                And (site.get_reputation () >= cls._REP, \
                    1.0 >= site.get_reputation () >= 0.0)) \
                    for site in sites])
        s.add ([Implies (Bool (site.get_name ()) == True, \
                And (Settings.BATTERY_LF >= (cls._BL - metrics[site]['ec']) \
                    / cls._BL >= 0.0)) for site in sites])
        s.add ([Implies (Bool (site.get_name ()) == True, \
                And (site.get_mem_consum () < 1, \
                    site.get_stor_consum () < 1)) \
                    for site in sites])

        access_vars = [Bool (site.get_name ()) for site in sites]

        return (s, access_vars)


    def __compute_metrics (cls, task, curr_n, off_sites, topology):
        
        metrics = list ()

        for cand_n in off_sites:
            (rsp_time, e_consum) = cls.__compute_objectives (task, cand_n, curr_n,\
                topology)
            metrics.append({cand_n: {'rsp': rsp_time, 'e_consum': e_consum}})

        return metrics


    def __compute_objectives (cls, task, cand_n, curr_n, topology):
        
        t_rsp_time = Model.task_rsp_time (task, cand_n, curr_n, topology)
        t_e_consum = Model.task_e_consum (t_rsp_time, cand_n, curr_n)

        return (t_rsp_time.get_overall (), t_e_consum.get_overall ())