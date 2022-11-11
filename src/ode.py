from abc import ABC, abstractmethod


class OffloadingDecisionEngine(ABC):

    def __init__(self, name, curr_n, md):
            
        self._name = name
        self._curr_n = curr_n
        self._md = md

        super().__init__()


    def get_name(cls):
        
        return cls._name


    @abstractmethod
    def offload(cls, tasks, off_sites, topology):
        
        pass