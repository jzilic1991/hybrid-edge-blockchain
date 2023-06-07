import random
import numpy


class MeasureUnits:
    
    KILOBYTE = 1000            # bytes
    KILOBYTE_PER_SECOND = 1000 # 1Mbps -> 0.125 Mb/s
    THOUSAND_MS = 1000         # 1000ms -> 1s used for network latency unit conversion
    GIGABYTES = 1000000
    HOUR_IN_SEC = 3600


class PowerConsum:

    # constants for power consumption (Watts)
    UPLINK = 1.3
    DOWNLINK = 1.0
    LOCAL = 0.9
    IDLE = 0.3


class Prices:

    STOR_PER_GB = 0.023 # american dollars (Google Cloud Storage for Central Europe [Warsaw])
    CPU_PER_HOUR = 0.776 # american dollars (Google Cloud general-purpose VMs)


class Settings:

    OFFLOADING_FAILURE_DETECTION_TIME = 1.5 # seconds
    BATTERY_LF = 1000 # joules
    SNR = 5 # dB
    ETA = 0.5
    W_RT = 0.5
    W_EC = 0.4
    W_PR = 0.1
    PROGRESS_REPORT_INTERVAL = 1
    K = 3
    EXECUTIONS = 100
    SAMPLES = 2
    NUM_LOCS = 5


class Testnets:

	KOVAN, ROPSTEN, RINKEBY, GOERLI, TRUFFLE, GANACHE = \
		('kovan', 'ropsten', 'rinkeby', 'goerli', 'truffle', 'ganache')


class PrivateKeys:

	TRUFFLE, GANACHE = \
		('1f41756c4f3d7abf3fc0c81c813e71d5e920d54acfe743bf99326935fabdf451', \
			'0x389496993f10af5a7c4b0af6310b09877894f5b26556b4016aafd3b345fe8f18')


class ExeErrCode:

    EXE_NOK, EXE_OK = range(2)


class TaskTypes:

    DI, CI, MODERATE = ('DI', 'CI', 'MODERATE')


class MobApps:

    #ANTIVIRUS, GPS_NAVIGATOR, CHESS, FACERECOGNIZER, FACEBOOK = \
    #	('ANTIVIRUS', 'GPS_NAVIGATOR', 'CHESS', 'FACERECOGNIZER', 'FACEBOOK')

    INTRASAFED, MOBIAR, NAVIAR = ('INTRASAFED', 'MOBIAR', 'NAVIAR')
    #PROBS = {ANTIVIRUS: 0.05, GPS_NAVIGATOR: 0.3, CHESS: 0.1, FACERECOGNIZER: 0.1, \
    #    FACEBOOK: 0.45}
    PROBS = {INTRASAFED: 0.25, MOBIAR: 0.4, NAVIAR: 0.35}


class NodeTypes:
    
    MOBILE, E_DATABASE, E_COMP, E_REG, CLOUD = ('Mobile Device', \
            'Edge Database Server', 'Edge Computational Server', \
            'Edge Regular Server', 'Cloud Data Center')


class NodePrototypes:

    MD, EC, ER, ED, CD = ('MD', 'EC', 'ER', 'ED', 'CD')


class OdeTypes:
    
    SMT, MDP, QRL = ('SMT', 'MDP', 'QRL')


class NetLinkTypes:

    WIRED, WIRELESS = ('WIRED', 'WIRELESS')


class OffActs:
    
    NUM_OFFLOAD_ACTS = 5
    MD, ED, EC, ER, CD = range(NUM_OFFLOAD_ACTS)


class OffloadingSiteCode:
    
    MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER,\
            UNKNOWN = range(6)


class OffloadingActions:
    
    NUMBER_OF_OFFLOADING_ACTIONS = 5
    MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER = \
        range(NUMBER_OF_OFFLOADING_ACTIONS)


class AvailabilityModes:
    
    HA, MA, LA = ("HA", "MA", "LA")


class Objective:
    
    def __init__ (self, execution, downlink, uplink, task_overall):
        
        self._execution = round (execution, 3)
        self._downlink = round (downlink, 3)
        self._uplink = round (uplink, 3)
        self._task_overall = round (task_overall, 3)

    
    def get_execution (cls):
        
        return cls._execution


    def get_downlink (cls):
        
        return cls._downlink


    def get_uplink (cls):
        
        return cls._uplink


    def get_overall (cls):
        
        return cls._task_overall


class ResponseTime (Objective):
    
    pass


class EnergyConsum (Objective):
    
    pass



class Util (object):

    @classmethod
    def determine_name_and_action (cls, offloading_site_code):
    
        if offloading_site_code == OffloadingSiteCode.EDGE_DATABASE_SERVER:
            return OffloadingActions.EDGE_DATABASE_SERVER

        elif offloading_site_code == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
            return OffloadingActions.EDGE_COMPUTATIONAL_INTENSIVE_SERVER

        elif offloading_site_code == OffloadingSiteCode.EDGE_REGULAR_SERVER:
            return OffloadingActions.EDGE_REGULAR_SERVER

        elif offloading_site_code == OffloadingSiteCode.CLOUD_DATA_CENTER:
            return OffloadingActions.CLOUD_DATA_CENTER

        elif offloading_site_code == OffloadingSiteCode.MOBILE_DEVICE:
            return OffloadingActions.MOBILE_DEVICE

        else:
            raise ValueError ("Offloading site code is invalid! (" + str(offloading_site_code) + ")")

    @classmethod
    def determine_off_site_code (cls, node_type):
        
        if isinstance (node_type, NodeTypes):
            return OffloadingSiteCode.UNKNOWN

        if node_type == NodeTypes.E_DATABASE:
            return OffloadingSiteCode.EDGE_DATABASE_SERVER
        
        elif node_type == NodeTypes.E_COMP:
            return OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER

        elif node_type == NodeTypes.E_REG:
            return OffloadingSiteCode.EDGE_REGULAR_SERVER
        
        elif node_type == NodeTypes.CLOUD:
            return OffloadingSiteCode.CLOUD_DATA_CENTER

        elif node_type == NodeTypes.MOBILE:
            return OffloadingSiteCode.MOBILE_DEVICE

        else:
            return OffloadingSiteCode.UNKNOWN


    @classmethod
    def determine_node_prototype (cls, node_type):

        if node_type == NodeTypes.E_DATABASE:
            return NodePrototypes.ED
        
        elif node_type == NodeTypes.E_COMP:
            return NodePrototypes.EC

        elif node_type == NodeTypes.E_REG:
            return NodePrototypes.ER
        
        elif node_type == NodeTypes.CLOUD:
            return NodePrototypes.CD

        elif node_type == NodeTypes.MOBILE:
            return NodePrototypes.MD


    @classmethod
    def generate_di_cpu_cycles(cls):

        return random.randint(100, 200)


    @classmethod
    def generate_ci_cpu_cycles(cls):

        return random.randint(750, 850)


    @classmethod
    def generate_random_cpu_cycles(cls):

        return random.randint(100, 200)


    @classmethod
    def generate_di_input_data(cls):

        return random.randint(4 * 35, 4 * 50)


    @classmethod
    def generate_random_input_data(cls):

        return random.randint(4, 8)


    @classmethod
    def generate_ci_input_data(cls):

        return random.randint(2, 4)


    @classmethod
    def generate_di_output_data(cls):

        return random.randint(4 * 25, 4 * 30)


    @classmethod
    def generate_random_output_data(cls):

        return random.randint(4, 8)


    @classmethod
    def generate_ci_output_data(cls):

        return random.randint(4, 8)


    @classmethod
    def get_lat (cls, f_peer, s_peer):
        
        if f_peer.get_node_type() == NodeTypes.CLOUD and \
            s_peer.get_node_type() == NodeTypes.E_DATABASE:
            
            return round((15 + numpy.random.normal(200, 33.5)), 2)

        if f_peer.get_node_type() == NodeTypes.CLOUD and \
            s_peer.get_node_type() == NodeTypes.E_COMP:
            
            return round((15 + numpy.random.normal(200, 33.5)), 2)

        if f_peer.get_node_type() == NodeTypes.CLOUD and \
            s_peer.get_node_type() == NodeTypes.E_REG:
            
            return round((15 + numpy.random.normal(200, 33.5)), 2)

        if f_peer.get_node_type() == NodeTypes.CLOUD and \
            s_peer.get_node_type() == NodeTypes.MOBILE:
            
            return round((54 + numpy.random.normal(200, 33.5)), 2)

        if f_peer.get_node_type() == NodeTypes.E_DATABASE and \
            s_peer.get_node_type() == NodeTypes.E_COMP:
            
            return 10

        if f_peer.get_node_type() == NodeTypes.E_DATABASE and \
            s_peer.get_node_type() == NodeTypes.E_REG:
            
            return 10

        if f_peer.get_node_type() == NodeTypes.E_DATABASE and \
            s_peer.get_node_type() == NodeTypes.MOBILE:
            
            return 15

        if f_peer.get_node_type() == NodeTypes.E_COMP and \
            s_peer.get_node_type() == NodeTypes.E_REG:
            
            return 10 

        if f_peer.get_node_type() == NodeTypes.E_COMP and \
            s_peer.get_node_type() == NodeTypes.MOBILE:
            
            return 15

        if f_peer.get_node_type() == NodeTypes.E_REG and \
            s_peer.get_node_type() == NodeTypes.MOBILE:
            
            return 15


    @classmethod
    def get_edge_sites (cls, off_sites):

        e_sites = list ()

        for site in off_sites:

            n_t = site.get_node_type ()

            if n_t == NodeTypes.E_DATABASE or n_t == NodeTypes.E_REG or\
                n_t == NodeTypes.E_COMP:

                e_sites.append (site)

        return e_sites



    @classmethod
    def get_cloud_sites (cls, off_sites):

        c_sites = list ()

        for site in off_sites:

            if site.get_node_type () == NodeTypes.CLOUD:

                c_sites.append (site)

        return c_sites



    @classmethod
    def get_mob_site (cls, off_sites):

        for site in off_sites:

            if site.get_node_type () == NodeTypes.MOBILE:

                return site

        return None
