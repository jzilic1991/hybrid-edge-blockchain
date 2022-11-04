import sys

from util import Util, NodeTypes, ExeErrCode
from task import Task


class OffloadingSite:

    def __init__(self, name_id, data):

        self._name_id = name_id
        self._mips = data['mips']
        self._mem = data['mem']
        self._stor = data['stor']
        self._stor_consum = 0
        self._mem_consum = 0
        self._node_type = data['type']
        self._url = data['url']
        self._time_epoch_cnt = 0
        
        # self.print_system_config()


    def print_system_config(cls):
        
        print ("################### " + cls._name_id  +" SYSTEM CONFIGURATION ###################", file = sys.stdout)
        print ("Name: " + cls._name_id, file = sys.stdout)
        print ("CPU: " + str(cls._mips) + " M cycles", file = sys.stdout)
        print ("Memory: " + str(cls._mem) + " Gb", file = sys.stdout)
        print ("Data Storage: " + str(cls._stor) + " Gb", file = sys.stdout)
        print ("Node type: " + str(cls._node_type), file = sys.stdout)
    

    def get_node_type (cls):
        
        return cls._node_type


    def get_n_id (cls):
        
        return cls._name_id
    

    def get_mips (cls):
        
        return cls._mips
    

    def time_epoch_count (cls):
        
        cls._time_epoch_cnt += 1


    def check_valid_deploy(cls, task):
        
        if not isinstance(task, Task):
            return ExeErrCode.EXE_NOK

        # check that task resouce requirements fits offloading sites's resource capacity
        if cls._stor > (cls._stor_consum + ((task.get_data_in() + task.get_data_out()) / GIGABYTES)) and \
            cls._mem > (cls._mem_consum + task.get_memory()):
            return ExeErrCode.EXE_OK