from z3 import *
import random
import math
import time

from ode import OffloadingDecisionEngine
from task import Task
from util import NodeTypes, Settings
from models import Model


class SqOde (OffloadingDecisionEngine):

    def __init__(self, name, curr_n, md, app_name, con_delay):

        self._k = Settings.K
        super().__init__(name, curr_n, md, app_name, con_delay)


    def offloading_decision(cls, task, metrics, timestamp, app_name, constr, qos, cell_name):

        k = cls._k

        if task.is_offloadable ():
            while True:
                start = time.time ()                
                top_k_sites = cls.__get_top_k_rep ([off_site for off_site in metrics.keys ()], k)
                # print ("Top k sites ")
                # for site in top_k_sites:
                #     print ("Site: " + site.get_n_id () + ", reputation: " + str (site.get_reputation ()))
                queue_wait_t = Model.queue_waiting_time (task, top_k_sites)
                best_off_site = cls.__select_best_one (queue_wait_t, timestamp)
                end = time.time ()

                # storing offloading decision time measurement
                if cls._measure_off_dec_time:
                  cls._cell_stats[cell_name].add_overhead (round (end - start, 6))
                  cls._measure_off_dec_time = False
                
                if best_off_site == None:
                    k = len (metrics)
                    continue

                return (best_off_site, metrics[best_off_site])

        for key, values in metrics.items ():
            if key.get_node_type() == NodeTypes.MOBILE:
                return (key, values)


    def __get_top_k_rep (cls, off_sites, k):

        return sorted (off_sites, key = lambda x: x.get_reputation (), reverse = True)[:k]


    def __select_best_one (cls, queue_wait_t, timestamp):

        min_w_t = None
        best_off_site = None

        for off_site, q_wait_t in queue_wait_t.items ():

            # print ("Offloading site: " + off_site.get_n_id ())
            # print ("Queue wait time: " + str (q_wait_t))
            # print ("Min waiting time: " + str (min_w_t))
            # print ("Avaialbility: " + str (off_site.avail_or_not (timestamp)))

            if (min_w_t == None or min_w_t > q_wait_t): #and off_site.avail_or_not (timestamp):

                min_w_t = q_wait_t
                best_off_site = off_site

        return best_off_site
