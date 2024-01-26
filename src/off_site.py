import sys
import random
import uuid
import numpy as np

from util import Util, NodeTypes, ExeErrCode, MeasureUnits, MobApps
from task import Task


class OffloadingSite:

    def __init__(self, p_id, data):
        
        self._name_id = p_id + str (uuid.uuid4 ())
        self._p_id = p_id
        self._mips = data['mips']
        self._cores = data['cores']
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
        self._off_action = Util.determine_name_and_action (self._off_site_code)
        self._node_prototype = Util.determine_node_prototype (self._node_type)
        self._dataset_node = None
        
        # self.print_system_config()

    def get_constr (cls, app_name):

        if app_name == MobApps.INTRASAFED:

            return cls._intra_constr

        elif app_name == MobApps.MOBIAR:

            return cls._mobiar_constr

        elif app_name == MobApps.NAVIAR:

            return cls._naviar_constr


    def avail_or_not (cls, t):

        return cls._dataset_node.is_avail_or_not (t)


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


    def get_node_prototype (cls):

        return cls._node_prototype


    def get_sc_id (cls):

        return cls._sc_id
    

    def get_node_type (cls):
        
        return cls._node_type


    def get_reputation (cls):

        # if cls._node_type == NodeTypes.MOBILE:
            
        #     return 1.0
        
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
            not cls._dataset_node.is_avail_or_not (t):
                
            return ExeErrCode.EXE_NOK
        
        if not task.execute():
                
            raise ValueError("Task execution operation is not executed properly! Please check the code of execute() method in Task class!")

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

    def gen_workload (cls, pois_rate, exp_rate):

      # workload is generated only by mobile devices, otherwise workload is zero
      if cls._node_type == NodeTypes.MOBILE:

        return cls.__gen_task_size (exp_rate) * cls.__gen_numb_of_tasks (pois_rate)

      return 0.0


    def __gen_task_size (cls, exp_rate):

      return random.expovariate (exp_rate)


    def __gen_numb_of_tasks (cls, pois_rate):

      return np.random.poisson (lam = pois_rate)


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
