from z3 import *
import random
import math

from ode import OffloadingDecisionEngine
from task import Task
from util import NodeTypes, Settings
from models import Model


class SqOde (OffloadingDecisionEngine):

    def __init__(self, name, curr_n, md, app_name):

        self._k = Settings.K
        super().__init__(name, curr_n, md, app_name)


    def dynamic_t_incentive (cls, task, metric):

        incentive = int (round ((task.get_rt () - metric['rt']) / task.get_rt (), 3) * 1000)
        if incentive >= 0 and incentive <= 1000:

            return incentive

        return 0


    def offloading_decision(cls, task, metrics):
        
        if task.is_offloadable ():

            top_k_sites = cls.__get_top_k_rep ([off_site for off_site in metrics.keys ()])
            queue_wait_t = Model.queue_waiting_time (task, top_k_sites)
            best_off_site = cls.__select_best_one (queue_wait_t)
            return (best_off_site, metrics[best_off_site])

        for key, values in metrics.items ():
                
            if key.get_node_type() == NodeTypes.MOBILE:
                    
                return (key, values)


    def __get_top_k_rep (cls, off_sites):

        return sorted (off_sites, key = lambda x: x.get_reputation (), reverse = True)[:cls._k]


    def __select_best_one (cls, queue_wait_t):

        min_w_t = None
        best_off_site = None

        for off_site, q_wait_t in queue_wait_t.items ():

            if min_w_t == None or min_w_t > q_wait_t:

                min_w_t = q_wait_t
                best_off_site = off_site

        return best_off_site
