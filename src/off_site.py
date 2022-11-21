import sys
import random

from util import Util, NodeTypes, ExeErrCode, MeasureUnits
from task import Task


class OffloadingSite:

    def __init__(self, name_id, data):

        self._name_id = name_id
        self._mips = data['mips']
        self._cores = data['cores']
        self._mem = data['mem']
        self._stor = data['stor']
        self._cpu_consum = 0
        self._stor_consum = 0
        self._mem_consum = 0
        self._node_type = data['type']
        self._url = data['url']
        self._time_epoch_cnt = 0
        self._reput = 0
        self._sc_id = 0
        self._mal_behav = False
        
        # self.print_system_config()


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


    def set_mal_behav (cls, behav):

        cls._mal_behav = behav


    def get_sc_id (cls):

        return cls._sc_id
    

    def get_node_type (cls):
        
        return cls._node_type


    def get_reputation (cls):

        return cls._reput


    def get_behav (cls):

        return cls._mal_behav


    def get_cpu_consum (cls):

        return cls._cpu_consum


    def get_stor_consum (cls):

        return cls._stor_consum


    def get_mem_consum (cls):

        return cls._mem_consum


    def get_n_id (cls):
        
        return cls._name_id
    

    def get_mips (cls):
        
        return cls._mips


    def get_cores (cls):

        return cls._cores
    

    def time_epoch_count (cls):
        
        cls._time_epoch_cnt += 1


    def check_valid_deploy(cls, task):
        
        if not isinstance(task, Task):
            return ExeErrCode.EXE_NOK

        # check that task resouce requirements fits offloading sites's resource capacity
        if cls._stor > (cls._stor_consum + ((task.get_data_in() + task.get_data_out()) / GIGABYTES)) and \
            cls._mem > (cls._mem_consum + task.get_memory()):
            return ExeErrCode.EXE_OK


    def execute (cls, task):
            
        if not isinstance (task, Task):
                
            raise ValueError("Task for execution on offloading site should be Task class instance!")

        if (not task.is_offloadable() and cls._node_type != NodeTypes.MOBILE) or \
            cls._mal_behav:
                
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
