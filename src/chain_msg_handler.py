# user-defined libs
import os
import json
import time

from threading import Thread
from util import Testnets, PrivateKeys


# built-in libs
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider


class ChainMsgHandler :
	

	def __init__ (self, testnet):

		self.__prepare_basics (testnet)
		self.__prepare_threads ()


	def get_base (cls):

		return cls._smart_contract.functions.BASE().call()


	def get_reputation_score (cls, nodeid):

		return cls._smart_contract.functions.getReputationScore(nodeid).call()[0] / cls._base


	def register_node (cls, name):

		registration_event = cls._smart_contract.events.NodeRegistered ()
		tx = cls._smart_contract.functions.registerNode(name).buildTransaction({
		        'from': cls._account.address,
		        'gasPrice': cls._w3.eth.gas_price,
		        'nonce': cls._w3.eth.getTransactionCount (cls._account.address)
		    })

		signed_tx = cls._w3.eth.account.signTransaction (tx, cls._key)
		tx_hash = cls._w3.eth.sendRawTransaction (signed_tx.rawTransaction)
		tx_receipt = cls._w3.eth.waitForTransactionReceipt (tx_hash)
		result = registration_event.processReceipt(tx_receipt)
		
		return result[0]['args']


	def update_reputation_score (cls, transactions):

		# print ('Incentive: ' + str (incentive / cls._base))
		reputation_update_event = cls._smart_contract.events.ReputationUpdate ()
		tx = cls._smart_contract.functions.updateNodeReputation(transactions[0]['id'], transactions[0]['reward']).buildTransaction({
		        'from': cls._account.address,
		        'gasPrice': cls._w3.eth.gas_price,
		        'nonce': cls._w3.eth.getTransactionCount (cls._account.address)
		    })
		
		signed_tx = cls._w3.eth.account.signTransaction (tx, cls._key)
		start = time.time ()
		tx_hash = cls._w3.eth.sendRawTransaction (signed_tx.rawTransaction)
		tx_receipt = cls._w3.eth.waitForTransactionReceipt (tx_hash)
		result = reputation_update_event.processReceipt(tx_receipt)
		end = time.time ()
		# print ('Elapsed time is ' + str (round (end - start, 3)) + ' s')
		print ("Current reputation score for " + node['name'] + " (id: " + str (node["id"]) + ") is " + 
	        str (result[0]['args']['value'] / cls._base))


	async def deploy_smart_contract (cls):
		
		# load smart contract data structure
		truffle_file = json.load (open ('./build/contracts/Reputation.json'))
		abi = truffle_file['abi']
		bytecode = truffle_file['bytecode']
		cls._smart_contract = cls._w3.eth.contract (bytecode = bytecode, abi = abi)
		
		# deploy smart contract instance
		tx = cls._smart_contract.constructor().buildTransaction({ 
	        'from': cls._account.address, 
	        'nonce': cls._w3.eth.getTransactionCount (cls._account.address),
	        'gas': 1728712,
	        'gasPrice': cls._w3.toWei (21, 'gwei')
	    })
	    
		signed_tx = cls._account.signTransaction (tx)
		tx_hash = cls._w3.eth.sendRawTransaction (signed_tx.rawTransaction)
		tx_receipt = cls._w3.eth.waitForTransactionReceipt (tx_hash)
		contract_address = tx_receipt.contractAddress
		cls._smart_contract = cls._w3.eth.contract (address = contract_address, abi = abi)
		# print ("Smart contract is deployed: " + str(tx_receipt))

		cls._base = cls._smart_contract.functions.BASE().call()

		return cls._smart_contract.address


	def __prepare_basics (cls, testnet):

		# load environment variables
		load_dotenv()

		# determine a test network for deploying the smart contract
		if testnet == Testnets.KOVAN:
			cls._testnet = 'https://kovan.infura.io/v3/' + os.environ['INFURA_API_KEY']
			
		elif testnet == Testnets.ROPSTEN:
			cls._testnet = 'https://ropsten.infura.io/v3/' + os.environ['INFURA_API_KEY']

		elif testnet == Testnets.RINKEBY:
			cls._testnet = 'https://rinkeby.infura.io/v3/' + os.environ['INFURA_API_KEY']

		elif testnet == Testnets.TRUFFLE:
			cls._testnet = 'http://localhost:9545'

		elif testnet == Testnets.GANACHE:
			cls._testnet = 'http://localhost:8545'

		else:
			raise ValueError ('Wrong testnet argument! Arg: ' + str (testnet))

		# establish web3 connection to the test network
		cls._w3 = Web3 (HTTPProvider (cls._testnet))
		print ("Web3 is connected: " + str(cls._w3.isConnected ()))

		# determine a user account based on a private key
		if testnet == Testnets.KOVAN or testnet == Testnets.ROPSTEN or testnet == Testnets.RINKEBY:
			cls._key = os.environ['PRIVATE_KEY']

		elif testnet == Testnets.TRUFFLE:
			cls._key = PrivateKeys.TRUFFLE_PRIVATE_KEY

		elif testnet == Testnets.GANACHE:
			cls._key = ''

		cls._account = cls._w3.eth.account.privateKeyToAccount (cls._key)


	def __prepare_threads (cls):
		t1 = Thread(target = cls.deploy_smart_contract)
		t1.start ()