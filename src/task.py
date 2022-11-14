import sys

from util import ExeErrCode, TaskTypes, Util
# from logger import Logger


class Task:
    
    def __init__(self, name, data):

        self._name = name
        self._memory = data['memory']
        self._off = data['offload']
        self._type = data['type']
        self._qos = data['qos']
        self._in_edges = []
        self._out_edges = []
        self._execute = False

        (self._mi, self._data_in, self._data_out) = \
            self.__determine_resources (self._type)

        # self.print_system()


    def get_name(cls):
        return cls._name


    def add_in_edge (cls, task):
        cls._in_edges.append(task)


    def add_out_edge (cls, task):
        cls._out_edges.append(task)


    def get_in_edges (cls):
        return cls._in_edges


    def get_out_edges (cls):
        return cls._out_edges


    def execute(cls):

        if cls._execute:
            return ExeErrCode.EXE_NOK
        
        elif cls._in_edges:
            return ExeErrCode.EXE_NOK
        
        else:

            for task in cls._out_edges:

                if not task.remove_in_edge(cls):
                    return ExeErrCode.EXE_NOK

            cls._out_edges = []
            cls._execute = True

            return ExeErrCode.EXE_OK


    def is_executed (cls):
        
        return cls._execute


    def is_offloadable (cls):
        
        return cls._off


    def print_dependencies(cls):
        
        print ("################### " + cls._name + " DEPENDENCIES ###################", file = sys.stdout)
    
        print ("***INPUT DEPENDENCIES***", file = sys.stdout)
        for edge in cls._in_edges:
            print (edge, file = sys.stdout)
        print ('\n', file = sys.stdout)

        print ("***OUTPUT DEPENDECIES***", file = sys.stdout)
        for edge in cls._out_edges:
            print (edge, file = sys.stdout)
        print ('\n', file = sys.stdout)

        print ('\n\n', file = sys.stdout)

    
    def print_system(cls):
        
        print ("######### " + cls._name + " SYSTEM CONFIGURATION #########")
        print ("CPU: " + str(cls._mi) + " M cycles")
        print ("Memory: " + str(cls._memory) + " Gb")
        print ("Input data: " + str(cls._data_in) + " Kb")
        print ("Output data: " + str(cls._data_out) + " Kb")
        print ("Offloadable: Yes" if cls._off else "Offloadable: No")
        print ("QoS: " + str(cls._qos) + "\n")
        

    def remove_in_edge(cls, executed_task):
        
        if executed_task in cls._in_edges:
            cls._in_edges.remove(executed_task)
            return True
        else:
            return False


    def reset(cls):
        
        cls._execute = False


    def get_data_in(cls):
        
        return cls._data_in


    def get_data_out(cls):
        
        return cls._data_out 


    def get_mi(cls):
        
        return cls._mi


    def get_memory(cls):
        
        return cls._memory


    def get_rt (cls):

        return cls._qos['rt']


    def get_ec (cls):

        return cls._qos['ec']


    def get_pr (cls):

        return cls._qos['pr']


    def get_type (cls):

        return cls._type


    def __determine_resources (cls, task_type):
        
        if task_type == TaskTypes.MODERATE:
            cpu_cycles = Util.generate_random_cpu_cycles ()
            input_data = Util.generate_random_input_data ()
            output_data = Util.generate_random_output_data ()

        elif task_type == TaskTypes.DI:
            cpu_cycles = Util.generate_di_cpu_cycles ()
            input_data = Util.generate_di_input_data ()
            output_data = Util.generate_di_output_data ()

        elif task_type == TaskTypes.CI:
            cpu_cycles = Util.generate_ci_cpu_cycles ()
            input_data = Util.generate_ci_input_data ()
            output_data = Util.generate_ci_output_data ()

        return (cpu_cycles, input_data, output_data)