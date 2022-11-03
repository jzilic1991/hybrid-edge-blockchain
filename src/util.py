import random


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