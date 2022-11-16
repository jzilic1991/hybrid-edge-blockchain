from abc import ABC, abstractmethod


class OffloadingDecisionEngine(ABC):

    def __init__(self, name, curr_n, md):
            
        self._name = name
        self._curr_n = curr_n
        self._md = md

        super().__init__()


    def get_name(cls):
        
        return cls._name


    def get_current_site (cls):

        return cls._curr_n


    def get_md (cls):

        return cls._md


    @abstractmethod
    def offload(cls, tasks, off_sites, topology):
        
        pass