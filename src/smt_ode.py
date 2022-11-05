import random

from ode import OffloadingDecisionEngine
from models import Model
from task import Task


class SmtOde(OffloadingDecisionEngine):

    def __init__(self, name, curr_n):

        super().__init__(name, curr_n)


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
                cand_n = cls.__offloading_decision (task, metrics)
                
                t_rsp_time = t_rsp_time + metrics[cand_n]['rsp']
                t_e_consum = t_e_consum + metrics[cand_n]['e_consum']
                
                if cand_n.execute (task):

                    t_rsp_time_arr += (t_rsp_time,)
                    t_e_consum_arr += (t_e_consum,)
                    break

            cand_n.terminate (task)

        max_rsp_time = 0
        for time in t_rsp_time_arr:
            if max_rsp_time < time:
                max_rsp_time = time

        acc_e_consum = 0
        for e_consum in t_e_consum_arr:
            acc_e_consum = acc_e_consum + e_consum

        cls._curr_n = cand_n

        return (max_rsp_time, acc_e_consum)


    def __offloading_decision(cls, task, metrics):
        
        ele = random.choice (metrics)
        off_site, _ = ele.item ()

        return off_site 
    

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