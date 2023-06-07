import json
import random

from off_site import OffloadingSite
from util import NodeTypes, Util, NodePrototypes, AvailabilityModes
from dataset import LoadedData


class ResourceMonitor:

    def __init__ (self, scala):

        self._scala = scala
        self._off_sites = self.__init_off_sites ()
        self._topology = self.__create_topology (json.load \
            (open ('data/topology.json')))
        self._json_datasets = json.load (open ('data/mapping.json'))

        LoadedData.load_dataset ("data/SKYPE.avt")
        # starting with first dataset node per node type
        self._off_sites = self.load_datasets (0)


    def get_topology (cls):

        return cls._topology


    def get_edge_regs (cls):
        
        return cls.__get_off_site (NodeTypes.E_REG)


    def get_edge_dats (cls):
        
        return cls.__get_off_site (NodeTypes.E_DAT)


    def get_edge_comps (cls):
        
        return cls.__get_off_site (NodeTypes.E_COMP)


    def get_cloud_dc (cls):
        
        return cls.__get_off_site (NodeTypes.CLOUD)


    def get_md(cls):
        
        return cls.__get_off_site (NodeTypes.MOBILE)[0]


    def get_bw (cls, f_peer, s_peer):

        return cls._topology[f_peer.get_n_id () + \
            '-' + s_peer.get_n_id ()]['bw']


    def get_lat (cls, f_peer, s_peer):

        return cls._topology[f_peer.get_n_id () + \
            '-' + s_peer.get_n_id ()]['lat']


    def get_off_sites (cls):
        
        return cls._off_sites


    def load_datasets (cls, n):

        for off_site in cls._off_sites:

            # dataset nodes are not mapped to mobile device since it is assumed to be failure-free
            id_ = cls._json_datasets[off_site.get_node_prototype ()][n]['id']
            off_site.load_data (LoadedData.get_dataset_node (id_))

        return cls._off_sites


    def __create_topology (cls, data):
        
        topology = dict ()
        i = 0

        for key, val in data['topology'].items ():
            f_peer = None
            s_peer = None
                        
            for f in cls._off_sites:
                for s in cls._off_sites:
                    if f.get_p_id () == val['peers'][0] and \
                        s.get_p_id () == val['peers'][1]:
                        f_peer = f
                        s_peer = s
                        # break

                        topology[f_peer.get_n_id () + '-' + s_peer.get_n_id ()] = \
                            {'bw': val['bw'], 'lat': Util.get_lat (f_peer, s_peer), \
                             'type': val['type']}
                        i += 1

        return topology


    def __init_off_sites (cls):
        
        off_sites = list ()
        data = json.load (open ('data/off-sites.json'))

        for p_id, res in data['off-sites'].items ():

            if p_id == NodePrototypes.MD:

                off_sites.append (OffloadingSite (p_id, res))

            else:
                
                for i in range (cls._scala):
                    
                    off_sites.append (OffloadingSite (p_id, res))

        return off_sites


    def __get_off_site (cls, node_type):

        nodes = list ()

        for off_site in cls._off_sites:
            if off_site.get_node_type () == node_type:
                nodes.append (off_site)
        
        return nodes