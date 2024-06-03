import random
import math 
import mdptoolbox
import time 
import numpy as np

from ode import OffloadingDecisionEngine
from util import NodePrototypes, OffloadingSiteCode, ExeErrCode, OffloadingActions, ResponseTime, EnergyConsum
from task import Task
from models import Model


class MdpOde(OffloadingDecisionEngine):

    def __init__(self, name, curr_n, md, app_name, con_delay):

        super().__init__(name, curr_n, md, app_name, con_delay)
        self._mobile_device = md
        self._offloading_sites = list ()


    # when mobile device arrives in a new cell then offloading site list and MDP matrices  are updated
    def update_matrices (cls, off_sites):

        cls._offloading_sites = off_sites
        cls._mobile_device = None
        
        for i in range (len (cls._offloading_sites)):

            cls._offloading_sites[i].set_off_action_index (i)

            if cls._offloading_sites[i].get_node_prototype () == NodePrototypes.MD:

              cls._mobile_device = cls._offloading_sites[i]

        if cls._mobile_device == None:

          raise ValueError ("Mobile device instance was not found in the current cell location!")

        cls.__init_MDP_settings()


    def offloading_decision (cls, task, metrics, timestamp, app_name, constr, qos, cell_name):

        validity_vector = [cls._offloading_sites[i].avail_or_not (timestamp) \
            for i in range (len (cls._offloading_sites))]
        
        for off_site in cls._offloading_sites:
            if not off_site in metrics.keys ():
                validity_vector[off_site.get_offloading_action_index()] = False

        while True:
            if not task.is_offloadable():
                for i in range (len(validity_vector)):
                    if cls._offloading_sites[i].get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
                        validity_vector[i] = False

                return (cls._mobile_device, metrics[cls._mobile_device])

            offloading_site_index = cls._curr_n.get_offloading_action_index()

            start = time.time ()
            cls._policy = cls.__MDP_run(task, metrics, validity_vector)
            # Logger.w("Current node: " + cls._current_node.get_name())
            # Logger.w("Current offloading policy: " + str(cls._policy))
            end = time.time ()
            
            if cls._measure_off_dec_time:
              cls._cell_stats[cell_name].add_overhead (round (end - start, 6))
              cls._measure_off_dec_time = False
            
            if cls._policy[offloading_site_index] == OffloadingActions.MOBILE_DEVICE:
                return (cls._offloading_sites[cls._mobile_device.get_offloading_action_index()], \
                    metrics[cls._mobile_device])

            trans_prob = list ()
            action_index = cls._policy[offloading_site_index]
            source_node_index = cls._curr_n.get_offloading_action_index()
            P_matrix_columns = len(cls._P[action_index][source_node_index])
            # print("P matrix columns [action = " + str(action_index) + "][source_node = " + \
            #    str(source_node_index) + "] = " + str(cls._P[action_index][source_node_index]))
            # print ("State (source) index: " + str (source_node_index))
            # print ("Action (destination) index: " + str (action_index))
            # print ("Probability matrix: " + str (cls._P[action_index][source_node_index]))
            # print ("Mobile device action index: " + str (cls._mobile_device.get_offloading_action_index ()))
            for i in range(P_matrix_columns):
                # print ("P[" + str (action_index) + "][" + str (source_node_inex) + "][" + str (i) + "] = " + \
                #  str (cls._P[action_index][source_node_index][i]))

                if cls._P[action_index][source_node_index][i] != 0.0 and \
                    i != cls._mobile_device.get_offloading_action_index():
                    trans_prob.append (1.0)

                else:
                    trans_prob.append (0.0)
                
            if sum (trans_prob) == 0.0:
              trans_prob[cls._mobile_device.get_offloading_action_index ()] = 1.0

            # print ("Transition probabilities are :" + str (trans_prob))
            offloading_site_index = np.random.choice(P_matrix_columns, 1, p = trans_prob)[0]

            if cls._offloading_sites[offloading_site_index].get_offloading_site_code() == \
                OffloadingSiteCode.MOBILE_DEVICE:
                validity_vector[action_index] = False

                if any(validity_vector):
                    continue

                else:
                    offloading_site_index = cls._mobile_device.get_offloading_action_index()
                    break

            break

          
        return (cls._offloading_sites[offloading_site_index], \
            metrics[cls._offloading_sites[offloading_site_index]])


    def __init_MDP_settings(cls):

        cls._P = np.array([[[0.0 for i in range(len (cls._offloading_sites))] \
                for i in range(len(cls._offloading_sites))] for i in range(len(cls._offloading_sites))])
        cls._R = np.array([[[0.0 for i in range(len (cls._offloading_sites))] \
                for i in range(len(cls._offloading_sites))] for i in range(len(cls._offloading_sites))])
        cls._response_time_matrix = np.array([[[0.0 for i in range(len (cls._offloading_sites))] \
                for i in range(len(cls._offloading_sites))] for i in range(len(cls._offloading_sites))])

        # print ("Offloading sites: " + str(cls._offloading_sites))

        if (cls._P.size / cls._P[0].size) != len (cls._offloading_sites):
            raise ValueError("Size of P matrix is not correct! It should contain " + \
                str (len (cls._offloading_sites)) + " action submatrices but it has "+ \
                str (cls._P.size / cls._P[0].size) + ".")

        for i in range (len (cls._offloading_sites)):
            if math.ceil (cls._P[i].size / cls._P[i][0].size) != len(cls._offloading_sites):
                raise ValueError("Number of rows of each action submatrix should be equal to number of offloading sites! Offloading sites = " + \
                str (len (cls._offloading_sites)) + ", matrix rows = " + str(math.ceil(cls._P[i].size / cls._P[i][0].size)) + " for " + \
                str(i + 1) + ".action submatrix. P[" + str(i) + "] = " + str(cls._P[i]))

            for j in range(len(cls._offloading_sites)):
                if cls._P[i][j].size != len(cls._offloading_sites):
                    raise ValueError("Size of " + str(i + 1) + ".action submatrix row should be equal to number of offloading sites " +\
                            str(len(cls._offloading_sites)) + " but it is " + str(cls._P[i][j].size))

        cls._discount_factor = 0.96
        cls._policy = ()
        
        # print ('Init P matrix = ' + str(cls._P))
        # print ('Init R matrix = ' + str(cls._R))


    def __MDP_run(cls, task, metrics, validity_vector):
        
        cls.__update_P_matrix()
        cls.__update_R_matrix(task, metrics, validity_vector)

        # Logger.w("P = " + str(cls._P))
        # Logger.w("R = " + str(cls._R))

        PIA = mdptoolbox.mdp.PolicyIteration(cls._P, cls._R, cls._discount_factor)
        PIA.verbose = False
        PIA.run()
        return PIA.policy

    
    def __update_P_matrix(cls):
        
        for i in range(len (cls._offloading_sites)): 
            for j in range(math.ceil(cls._P[i].size / cls._P[i][0].size)):
                for k in range(math.ceil(cls._P[i][j].size / cls._P[i][j][0].size)): 
                    # print ("Offloading site : " + str(cls._offloading_sites[k].get_n_id ()) + " with action index "\
                    #    + str (cls._offloading_sites[k].get_offloading_action_index()))
                    # print ("i = " + str (i) + ", k = " + str (k))
                    if cls._offloading_sites[k].get_offloading_action_index() == i:
                        cls._P[i][j][k] = cls._offloading_sites[k].\
                            get_avail ()

                    elif cls._mobile_device.get_offloading_action_index() == k:
                        cls._P[i][j][k] = 1 - cls._offloading_sites[i].\
                            get_avail ()

                    else:
                        cls._P[i][j][k] = 0.0

                    # print ("P["+ str(i) + "][" + str(j) + "][" + str(k) + "] = " + str(cls._P[i][j][k]))

        # print ("P matrix: " + str (cls._P))
        # exit()


    def __update_R_matrix(cls, task, metrics, validity_vector):
        
        for i in range(len (cls._offloading_sites)):
            for j in range(math.ceil(cls._R[i].size / cls._R[i][0].size)): 
                for k in range(math.ceil(cls._R[i][j].size / cls._R[i][j][0].size)):
                    if cls._P[i][j][k] == 0.0 or not validity_vector[i]:
                        cls._R[i][j][k] = 0.0
                        cls._response_time_matrix[i][j][k] = 0.0
                        continue

                    task_rsp_time = metrics[cls._offloading_sites[k]]['rt']
                    #cls._OffloadingDecisionEngine__compute_complete_task_time_completion(task, \
                    #        cls._offloading_sites[k], cls._offloading_sites[j])
                    task_energy_consum = metrics[cls._offloading_sites[k]]['ec']
                    task_price = metrics[cls._offloading_sites[k]]['pr']
                    #cls._OffloadingDecisionEngine__compute_complete_energy_consumption\
                    #        (task_rsp_time, cls._offloading_sites[k], cls._offloading_sites[j])
                    task_time_completion_reward = Model.task_rsp_time_rwd(task_rsp_time)
                    #cls._OffloadingDecisionEngine__compute_task_time_completion_reward\
                    #        (task_rsp_time.get_task_overall())
                    task_energy_consumption_reward = Model.task_e_consum_rwd (task_energy_consum)
                    task_price_rwd = Model.task_price_rwd (task_price)
                    task_overall_reward = Model.overall_task_rwd (task_time_completion_reward, \
                        task_energy_consumption_reward, task_price_rwd)

                    if task_rsp_time < 0 or task_energy_consum < 0 or task_time_completion_reward < 0 or \
                            task_energy_consumption_reward < 0 or task_overall_reward < 0 or task_price_rwd < 0:
                        
                        raise ValueError("Some value is negative, leading to negative rewards!")

                    cls._R[i][j][k] = round(task_overall_reward, 3)
                    cls._response_time_matrix[i][j][k] = round(task_rsp_time, 3)


    # def __recovery_action(cls, validity_vector, action_index):
        
    #     validity_vector[action_index] = False
    #     return validity_vector
