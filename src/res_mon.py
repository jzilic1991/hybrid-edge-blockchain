import json
import random

from off_site import OffloadingSite
from util import NodeTypes, Util, NodePrototypes, AvailabilityModes, CommDirection, PoissonRate, ExpRate
from dataset import LoadedData
from edge_queue import CommQueue
from infra import Infrastructure


class ResourceMonitor:

    def __init__ (self, scala):

        self._scala = scala
        self._clustered_cells = Infrastructure.get_clustered_cells ("data/AT-Cell.csv", \
          json.load (open ("data/off-sites.json"))) 
        # self._off_sites = self.__init_off_sites ()
        #self._topology = self.__create_topology (json.load \
        #    (open ('data/topology.json')))
        self._json_datasets = json.load (open ('data/mapping.json'))
        LoadedData.load_dataset ("data/SKYPE.avt")
        # cell name is updated after loading dataset node
        self._curr_cell = ""
        # starting with first dataset node per node type
        # self._off_sites = self.load_datasets (0)


    def get_topology (cls):

        return cls._topology


    def get_cell_name (cls):

        return cls._curr_cell


    def get_edge_regs (cls, n):
        
        return cls.__get_off_site (NodeTypes.E_REG, n)


    def get_edge_dats (cls, n):
        
        return cls.__get_off_site (NodeTypes.E_DAT, n)


    def get_edge_comps (cls, n):
        
        return cls.__get_off_site (NodeTypes.E_COMP, n)


    def get_cloud_dc (cls, n):
        
        return cls.__get_off_site (NodeTypes.CLOUD, n)[0]


    def get_md (cls, n):
        
        return cls.__get_off_site (NodeTypes.MOBILE, n)[0]


    def get_bw (cls, f_peer, s_peer):

        return cls._topology[f_peer.get_n_id () + \
            '-' + s_peer.get_n_id ()]['bw']


    def get_lat (cls, f_peer, s_peer):

        return cls._topology[f_peer.get_n_id () + \
            '-' + s_peer.get_n_id ()]['lat']


    def get_off_sites (cls):
        
        return cls._off_sites


    def get_cell (cls, n):

        off_sites = cls._clustered_cells[n]
        
        # new datasets are loaded when mobile device is moved to a new cell
        for site in off_sites:

            # dataset nodes are not mapped to mobile device since it is assumed to be failure-free
            id_ = cls._json_datasets[site.get_node_prototype ()][n]['id']
            site.load_data (LoadedData.get_dataset_node (id_))

        # update cell name when new dataset nodes are loaded
        cls._curr_cell = n
        for site in off_sites:

            site.update_arrival_rate ()
            site.update_task_size_rate ()

        return off_sites


    # cell name is a concatination of all dataset node ids
    def __get_cell_name (cls):

        cell_name = ""

        for off_site in cls._off_sites:

            cell_name += off_site.get_dataset_info () + "\n"

        return cell_name


    def __create_topology (cls, data):
        
        topology = dict ()
        i = 0
        md_update_bw_flag = False

        for key, val in data['topology'].items ():
            f_peer = None # first peer
            s_peer = None # second peer
                        
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
                        
                        # if mobile device is a second peer node then the bandwidth of 
                        # first peer site will be taken as a communication queue length
                        # of both offloading and delivery queues
                        if s_peer.get_node_prototype () == NodePrototypes.MD:
                          
                          f_peer.set_bandwidth (val['bw'])

                          # set bandwidth for mobile device just once
                          if not md_update_bw_flag:

                            s_peer.set_bandwidth (235)
                            md_update_bw_flag = True

        return topology


    # instantiating offloading sites
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


    def __get_off_site (cls, node_type, n):

        nodes = list ()
        
        for off_site in cls._clustered_cells[n]:
            
            if off_site.get_node_type () == node_type:
              
              nodes.append (off_site)

        return nodes
