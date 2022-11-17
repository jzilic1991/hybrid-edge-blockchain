import sys

from task import Task
from util import ExeErrCode


class MobileApplication:

    def __init__(self, name, data):

        self._name = name
        self._app_struct = self.__json_to_dict (data['tasks'])
        self._qos = data['qos']
        self._running = False

        self.__init_task_dependencies ()
        # self.print_entire_config ()
        
        # for task in self._app_struct:
        #     task.print_system()


    def run(cls):

        if not cls._running:
            cls._running = True


    def get_name(cls):

        return cls._name

    
    def get_ready_tasks(cls):

        ready_tasks = ()

        if not cls._running:
            
            return ready_tasks

        for task in cls._app_struct:
            
            if not task.get_in_edges() and not task.is_executed():
                
                ready_tasks = ready_tasks + (task,)

        if not ready_tasks:
            
            for task in cls._app_struct:
                
                if not task.is_executed():
                    
                    return ready_tasks

            # cls.print_task_exe_status()
            cls.__init_task_dependencies()
            cls._running = False

        return ready_tasks


    def print_task_dependencies(cls):

        print("******** TASK DEPENDENCIES ********")
        
        for key, values in cls._app_struct.items():
            for value in values:
                print(key.get_name() + " ----------> " + value.get_name())
        
        print ('QoS: ' + str(cls._qos))
        print ('\n')


    def print_task_config(cls):
        
        for task in cls._app_struct:
            task.print_system()


    def print_task_exe_status(cls):
        
        print_text = ""

        for task in cls._app_struct:
            if task.is_executed():
                print_text = print_text + task.get_name() + "(" + \
                    str(task.is_offloadable()) + ")" + " is EXECUTED\n"

        print (print_text)

    
    def print_entire_config(cls):

        print("######## " + cls._name + " APPLICATION CONFIGURATION ##########")

        cls.print_task_dependencies()
        # cls.print_task_config()
        # cls.print_task_exe_status()


    def __json_to_dict (cls, data):

        app_struct = dict () # app dag structure
        lookup = list () # lookup table

        # iterate JSON task keys
        for t_name, t_data in data.items():
            # check task key exists in lookup table
            t_key = None
                
            for t in lookup:
                if t.get_name () == t_name:
                    t_key = t
                    break

            # if task key does not exist in lookup table
            if t_key == None:
                #(cpu, in_data, out_data) = \
                #    cls.__determine_resources(t_data['type'])
                
                t_key = Task (t_name, t_data)
                # t_key = data[t_name]
                lookup.append (t_key)

            # if task key does not exist in app struct then add it
            if not t_key in app_struct:
                app_struct[t_key] = list ()

            # iterate JSON task values
            for out in data[t_name]['out']:
                t_val = None

                # check does task value exists in lookup table
                for t in lookup:
                    if t.get_name () == out:
                        t_val = t
                        break

                # if task value does not exist in lookup table
                if t_val == None:
                    #(cpu, in_data, out_data) = \
                    #    cls.__determine_resources(t_data['type'])
                
                    t_val = Task (out, t_data)
                    # t_val = data[app_name]['tasks'][t_name]
                    lookup.append (t_val)

                # if key value does not exist in app struct then add it
                if not t_val in app_struct[t_key]:
                    app_struct[t_key].append (t_val)

        return app_struct


    def __init_task_dependencies(cls):
        
        for key, values in cls._app_struct.items():
            for value in values:
                key.add_out_edge (value)
                value.add_in_edge(key)
                
            key.reset()