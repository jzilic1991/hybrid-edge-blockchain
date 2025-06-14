import sys
import random
import uuid
import numpy as np

from util import NodePrototypes, ResponseTime, CommDirection, Util, NodeTypes, \
  ExeErrCode, MeasureUnits, MobApps, PoissonRate, ExpRate
from task import Task
from edge_queue import CompQueue, CommQueue
from workload_profiles import DefaultProfile, ARProfile

class OffloadingSite:
    def __init__(self, p_id, data, profile = "default"):
        self._name_id = p_id + str (uuid.uuid4 ())
        self._p_id = p_id
        self._mips = data['mips']
        self._cores = data['cores']
        self._bw = data['bw']
        self._mem = data['mem']
        self._stor = data['stor']
        self._intra_constr = IntraConstraints (data['proc-intra'], data['lat-intra'])
        self._mobiar_constr = MobiarConstraints (data['proc-mobiar'], data['lat-mobiar'])
        self._naviar_constr = NaviarConstraints (data['proc-naviar'], data['lat-naviar'])
        self._cpu_consum = 0
        self._stor_consum = 0
        self._mem_consum = 0
        self._node_type = data['type']
        self._url = data['url']
        self._time_epoch_cnt = 0
        self._reput = 1
        self._sc_id = 0
        self._off_site_code = Util.determine_off_site_code (self._node_type)
        self._off_action = None # offloading action index in MDP matrices
        self._node_prototype = Util.determine_node_prototype (self._node_type)
        self._dataset_node = None
        self.workload = None

        if profile == "ar":
            self.workload = ARProfile()
            #print(f"[EDGE QUEUE] Using AR workload profile")
        else:
            self.workload = DefaultProfile()
            #print(f"[EDGE QUEUE] Using default workload profile")

        #self._task_exe_queue = CompQueue (self._mips, arrival_rate = random.randint (PoissonRate.MIN_RATE, PoissonRate.MAX_RATE), \
        #  task_size_rate = random.uniform (ExpRate.MIN_RATE, ExpRate.MAX_RATE), site_name = self._node_type)
        self._task_exe_queue = CompQueue (self._mips, arrival_rate = self.workload.get_arrival_rate(), \
          task_size_rate = self.workload.get_task_size_rate(), site_name = self._node_type)
        # comm queues are initialized when bandwidth is set
        #self._task_off_queue = CommQueue (self._bw, arrival_rate = random.randint (PoissonRate.MIN_RATE, PoissonRate.MAX_RATE), \
        #  task_size_rate = random.uniform (ExpRate.MIN_RATE, ExpRate.MAX_RATE), comm_direct = CommDirection.UPLINK, \
        #  site_name = self._node_type)
        self._task_off_queue = CommQueue (self._bw, arrival_rate = self.workload.get_arrival_rate(), \
          task_size_rate = self.workload.get_task_size_rate(), comm_direct = CommDirection.UPLINK, \
          site_name = self._node_type)
        #self._task_del_queue = CommQueue (self._bw, arrival_rate = random.randint (PoissonRate.MIN_RATE, PoissonRate.MAX_RATE), \
        #  task_size_rate = random.uniform (ExpRate.MIN_RATE, ExpRate.MAX_RATE), comm_direct = CommDirection.DOWNLINK,
        #  site_name = self._node_type)
        self._task_del_queue = CommQueue (self._bw, arrival_rate = self.workload.get_arrival_rate(), \
          task_size_rate = self.workload.get_task_size_rate(), comm_direct = CommDirection.DOWNLINK,
          site_name = self._node_type)
        self._est_lat = None
        self._act_lat = None
        self._off_lat = None
        # self.print_system_config()


    def reset_latencies (cls):

      cls._off_lat = None
      cls._act_lat = None
      cls._est_lat = None


    def est_lat (cls, task, curr_n_id, curr_n_proto):

      off_lat = 0.0
      del_lat = 0.0

      if curr_n_id != cls._name_id or cls._node_prototype == NodePrototypes.CD:
        off_lat = cls._task_off_queue.est_lat (task)
        # del_lat = cls._task_del_queue.est_lat (task)
          
        if curr_n_proto == NodePrototypes.CD or cls._node_prototype == NodePrototypes.CD:
          off_lat += round ((15 + np.random.normal(200, 33.5)) / MeasureUnits.THOUSAND_MS, 2)
          # print ("Estimated Offloading latency including internet latency is " + str (off_lat))
          # print ("Estimated Offloading latency is " + str (off_lat))
          # del_lat += round ((15 + np.random.normal(200, 33.5)) / 1000, 2)

      if cls._node_prototype == NodePrototypes.MD:
        del_lat += round ((15 + np.random.normal(200, 33.5)) / 1000, 2)

      exe_lat = cls._task_exe_queue.est_lat (task)
      # print ("Offloading latency: " + str (off_lat))
      # print ("Execution latency: " + str (exe_lat))
      total_lat = ResponseTime (exe_lat, del_lat, off_lat, off_lat + exe_lat + del_lat)
      cls._off_lat = off_lat
      # print ("Full estimated offloading latency is " + str (cls._off_lat))
      cls._est_lat = total_lat

      # print (cls._node_type + " has ESTIMATED OFFLOADING LATENCY (" + task.get_name () + ") = "+ str (off_lat))
      # print (cls._node_type + " has ESTIMATED EXECUTION LATENCY (" + task.get_name () + ") = " + str (exe_lat))
      # print (cls._node_type + " has ESTIMATED DELIVERY LATENCY (" + task.get_name () + ") = " + str (del_lat))
      # print (cls._name_id + " has ESTIMATED TOTAL LATENCY (task = " + task.get_name () + ") = " + str (total_lat.get_overall ()))

      return total_lat


    def act_lat (cls, task, curr_n_id, curr_n_proto):

      off_lat = 0.0
      del_lat = 0.0

      if curr_n_id != cls._name_id or cls._node_prototype == NodePrototypes.CD:
        off_lat = cls._task_off_queue.act_lat (task)
        # del_lat = cls._task_del_queue.act_lat (task)
        
        if curr_n_proto == NodePrototypes.CD or cls._node_prototype == NodePrototypes.CD:
          off_lat += round ((15 + np.random.normal(200, 33.5)) / MeasureUnits.THOUSAND_MS, 2)
          # print ("Actual Offloading latency including internet latency is " + str (off_lat))
          # print ("Actual Offloading latency is " + str (off_lat))
          # del_lat += round ((15 + np.random.normal(200, 33.5)) / 1000, 2)
      
      exe_lat = cls._task_exe_queue.act_lat (task)
      total_lat = ResponseTime (exe_lat, del_lat, off_lat, off_lat + exe_lat + del_lat)
      cls._off_lat = off_lat
      # print ("Full actual offloading latency is " + str (cls._off_lat))
      cls._act_lat = total_lat
      # print ("Total task latency time is " + str (total_lat.get_overall ()) + " s")      
      # print (cls._node_type + " has ACTUAL OFFLOADING LATENCY (" + task.get_name () + ") = " + str (off_lat))
      # print (cls._node_type + " has ACTUAL EXECUTION LATENCY (" + task.get_name () + ") = " + str (exe_lat))
      # print (cls._node_type + " has ACTUAL DELIVERY LATENCY (" + task.get_name () + ") = " + str (del_lat))
      # print (cls._name_id + " has ACTUAL TOTAL LATENCY (task = " + task.get_name () + ") = " + str (total_lat.get_overall ()))

      return total_lat


    def get_lat (cls):

      if cls._act_lat != None:
        return cls._act_lat

      return cls._est_lat


    def get_off_lat (cls):

      return cls._off_lat


    def update_arrival_rate (cls): 

      cls._task_off_queue.update_arrival_rate ()
      cls._task_exe_queue.update_arrival_rate ()
      cls._task_del_queue.update_arrival_rate ()


    def update_task_size_rate (cls):

      cls._task_off_queue.update_task_size_rate ()
      cls._task_exe_queue.update_task_size_rate ()
      cls._task_del_queue.update_task_size_rate ()


    def set_off_action_index (cls, index):

      cls._off_action = index        

    
    def set_bandwidth (cls, bw):
      
      pass
      # print (cls._name_id + " has updated bandwidth of both queues (offloading and delivery): " + str (bw))
     

    def workload_update (cls, time_passed):

      #print (cls._node_type + " workload update!")
      #print ("Time passed: " + str (time_passed))
      # print ("*** " + cls._name_id  + " queue state updates ***")
      cls._task_off_queue.workload_update (time_passed)
      cls._task_exe_queue.workload_update (time_passed)
      cls._task_del_queue.workload_update (time_passed)


    def get_constr (cls, app_name):

        if app_name == MobApps.INTRASAFED:
            return cls._intra_constr

        elif app_name == MobApps.MOBIAR:
            return cls._mobiar_constr

        elif app_name == MobApps.NAVIAR:
            return cls._naviar_constr


    def avail_or_not (cls, t):
        
        if cls._node_type != NodeTypes.MOBILE:
          return cls._dataset_node.is_avail_or_not (t)

        return True


    def get_avail (cls):

        return cls._dataset_node.get_avail ()


    def print_system_config(cls):
        
        print ("################### " + cls._name_id  +" SYSTEM CONFIGURATION ###################", file = sys.stdout)
        print ("Name: " + cls._name_id, file = sys.stdout)
        print ("CPU: " + str(cls._mips) + " M cycles", file = sys.stdout)
        print ("Memory: " + str(cls._mem) + " Gb", file = sys.stdout)
        print ("Data Storage: " + str(cls._stor) + " Gb", file = sys.stdout)
        print ("Node type: " + str(cls._node_type), file = sys.stdout)


    def set_sc_id (cls, sc_id):

        cls._sc_id = sc_id


    def set_reputation (cls, reput):
        
        cls._reput = reput
        # print ("SC ID " + str (cls._sc_id) + " has a reputation " + str (cls._reput))


    def get_node_prototype (cls):

        return cls._node_prototype


    def get_sc_id (cls):

        return cls._sc_id
    

    def get_node_type (cls):
        
        return cls._node_type


    def get_reputation (cls):

        return cls._reput


    def get_cpu_consum (cls):

        return cls._cpu_consum


    def get_stor_consum (cls):

        return cls._stor_consum


    def get_mem_consum (cls):

        return cls._mem_consum


    def get_n_id (cls):
        
        return cls._name_id


    def get_p_id (cls):

        return cls._p_id
    

    def get_mips (cls):
        
        return cls._mips


    def get_cores (cls):

        return cls._cores


    def get_offloading_action_index(cls):

        return cls._off_action


    def get_offloading_site_code (cls):

        return cls._off_site_code
    

    def time_epoch_count (cls):
        
        cls._time_epoch_cnt += 1


    def load_data (cls, dataset_node):

        cls._dataset_node = dataset_node
        # cls._dataset_node.print_dataset_info (cls._node_type)

    def get_dataset_info (cls):

        return cls._dataset_node.get_dataset_info (cls._node_type)


    def check_valid_deploy(cls, task):
        
        if not isinstance(task, Task):
            return ExeErrCode.EXE_NOK

        # check that task resouce requirements fits offloading sites's resource capacity
        if cls._stor > (cls._stor_consum + ((task.get_data_in() + task.get_data_out()) / GIGABYTES)) and \
            cls._mem > (cls._mem_consum + task.get_memory()):
            return ExeErrCode.EXE_OK


    def execute (cls, task, t):
            
        if not isinstance (task, Task):
            raise ValueError("Task for execution on offloading site should be Task class instance!")

        # print ("Offloadable: " + str(task.is_offloadable()) + ", node type: " + str(cls._node_type) + \
        #  ", avail: " + str(cls._dataset_node.is_avail_or_not (t)))
        if (not task.is_offloadable() and cls._node_type != NodeTypes.MOBILE) or \
            (not cls._dataset_node.is_avail_or_not (t) and cls._node_type != NodeTypes.MOBILE):
            return ExeErrCode.EXE_NOK
        
        if not task.execute():
            raise ValueError("Task execution operation is not executed properly! Please check the code of execute() method in Task class!")

        # consumption update
        cls._cpu_consum = cls._cpu_consum + (task.get_mi () / (cls._cores * cls._mips))
        cls._stor_consum = cls._stor_consum + \
            ((task.get_data_in() + task.get_data_out()) / MeasureUnits.GIGABYTES)
        cls._mem_consum = cls._mem_consum + task.get_memory()

        return ExeErrCode.EXE_OK


    def terminate (cls, task):
        
        if not isinstance(task, Task):
            
            return ExeErrCode.EXE_NOK
    
        cls._cpu_consum = cls._cpu_consum - (task.get_mi () / (cls._cores * cls._mips))
        cls._mem_consum = cls._mem_consum - task.get_memory()
        cls._stor_consum = cls._stor_consum - \
            ((task.get_data_in() + task.get_data_out()) / MeasureUnits.GIGABYTES)

        if cls._mem_consum < 0 or cls._stor_consum < 0:
            
            raise ValueError("Memory consumption: " + str(cls._mem_consum) + \
                    "Gb, data storage consumption: " + str(cls._stor_consum) + \
                    "Gb, both should be positive! Node: " + cls._name + ", task: " + \
                    task.get_name())

    # def gen_workload (cls):

    #  return cls.__gen_task_size (cls._exp_rate) * cls.__gen_numb_of_tasks (cls._arrival_rate)


class Constraints:

    def __init__ (self, proc, lat):

        self._proc = proc
        self._lat = lat


    def get_proc (cls):

        return cls._proc


    def get_lat (cls):

        return cls._lat


class IntraConstraints (Constraints):

    pass


class MobiarConstraints (Constraints):

    pass


class NaviarConstraints (Constraints):

    pass
