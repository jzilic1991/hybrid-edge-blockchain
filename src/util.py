import random
import numpy


class Testnets:

	KOVAN, ROPSTEN, RINKEBY, GOERLI, TRUFFLE, GANACHE = \
		('kovan', 'ropsten', 'rinkeby', 'goerli', 'truffle', 'ganache')


class PrivateKeys:

	TRUFFLE, GANACHE = \
		('1fa675ea7b5ef3c0b798dba0e0723302cf7e6d93f8556b9ebc924c633f81cdd0', \
			'0ac7f1a3f38e2dce973153179af82314b04657342383b8353f267ec4218727a6')


class ExeErrCode:

    EXE_NOK, EXE_OK = range(2)


class TaskTypes:

    DI, CI, MODERATE = ('DI', 'CI', 'MODERATE')


class MobApps:

    ANTIVIRUS, GPS_NAVIGATOR, CHESS, FACERECOGNIZER, FACEBOOK = \
    	('ANTIVIRUS', 'GPS_NAVIGATOR', 'CHESS', 'FACERECOGNIZER', 'FACEBOOK')


class NodeTypes:
    
    MOBILE, E_DATABASE, E_COMP, E_REG, CLOUD = ('Mobile Device', \
            'Edge Database Server', 'Edge Computational Server', \
            'Edge Regular Server', 'Cloud Data Center')


class OdeTypes:
    
    SMT, MDP, QRL = ('SMT', 'MDP', 'QRL')


class OffActs:
    
    NUM_OFFLOAD_ACTS = 5
    MD, ED, EC, ER, CD = range(NUM_OFFLOAD_ACTS)


class Util(object):

    @classmethod
    def generate_di_cpu_cycles(cls):

        return random.randint(100, 200)


    @classmethod
    def generate_ci_cpu_cycles(cls):

        return random.randint(550, 650)


    @classmethod
    def generate_random_cpu_cycles(cls):

        return random.randint(100, 200)


    @classmethod
    def generate_di_input_data(cls):

        return random.randint(4 * 25, 4 * 30)


    @classmethod
    def generate_random_input_data(cls):

        return random.randint(4, 8)


    @classmethod
    def generate_ci_input_data(cls):

        return random.randint(4, 8)


    @classmethod
    def generate_di_output_data(cls):

        return random.randint(4 * 15, 4 * 20)


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