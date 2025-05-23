# built-in libs
import os
import json
import time

# third-party libs
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.exceptions import ContractLogicError

# user-defined libs
from util import Testnets, PrivateKeys

class ChainHandler:
  def __init__ (self, testnet, port = 8545):
    self.__prepare_basics (testnet, port)

  def get_base (cls):
    return cls._smart_contract.functions.BASE().call()

  def get_reputation (cls, nodeId):
    try:
      return cls._smart_contract.functions.getReputationScore(nodeId).call()[0] / cls._base
    except ContractLogicError as e:
      print ("Contract logic error occured: " + str (e))
      return None

  def register_node (cls, nodeId):
    registration_event = cls._smart_contract.events.NodeRegistered ()
    tx = cls._smart_contract.functions.registerNode(nodeId).build_transaction({
        'from': cls._account,
        'gasPrice': cls._w3.eth.gas_price,
        'nonce': cls._w3.eth.get_transaction_count(cls._account)
    })
    tx_hash = cls._w3.eth.send_transaction(tx)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt(tx_hash)
    result = registration_event.process_receipt(tx_receipt)
    return result[0]['args']

  def unregister_node (cls, nodeId):
    registration_event = cls._smart_contract.events.NodeUnregistered()
    tx = cls._smart_contract.functions.unregisterNode(nodeId).build_transaction({
        'from': cls._account,
        'gasPrice': cls._w3.eth.gas_price,
        'nonce': cls._w3.eth.get_transaction_count(cls._account)
    })
    tx_hash = cls._w3.eth.send_transaction(tx)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt(tx_hash)
    result = registration_event.process_receipt(tx_receipt)
    return result[0]['args']

  async def update_reputation(cls, transactions):
    reputation_update_event = cls._smart_contract.events.ReputationUpdate()
    tx = cls._smart_contract.functions.updateNodeReputation(transactions).build_transaction({
        'from': cls._account,
        'gasPrice': cls._w3.eth.gas_price,
        'nonce': cls._w3.eth.get_transaction_count(cls._account)
    })
    tx_hash = cls._w3.eth.send_transaction(tx)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt(tx_hash)
    result = reputation_update_event.process_receipt(tx_receipt)
    event = result[0]['args']
    
    response = []
    for i in range(len(event.rsp)):
        response.append({'id': event.rsp[i].id, 'score': event.rsp[i].value / cls._base})
    
    return response
  
  def reset_reputation(cls, ids):
    reset_event = cls._smart_contract.events.ResetReputation()
    tx = cls._smart_contract.functions.resetReputations(ids).build_transaction({
        'from': cls._account,
        'gasPrice': cls._w3.eth.gas_price,
        'nonce': cls._w3.eth.get_transaction_count(cls._account)
    })
    tx_hash = cls._w3.eth.send_transaction(tx)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt(tx_hash)
    result = reset_event.process_receipt(tx_receipt)
    event = result[0]['args']
    
    response = []
    for i in range(len(event.rsp)):
        response.append({'id': event.rsp[i].id, 'score': event.rsp[i].value / cls._base})
    
    return response

  def deploy_smart_contract(cls):
    # load smart contract data structure
    truffle_file = json.load(open('.././build/contracts/Reputation.json'))
    abi = truffle_file['abi']
    bytecode = truffle_file['bytecode']
    
    contract_factory = cls._w3.eth.contract(bytecode=bytecode, abi=abi)

    tx = contract_factory.constructor().build_transaction({
        'from': cls._account,
        'nonce': cls._w3.eth.get_transaction_count(cls._account),
        'gas': 1728712,
        'gasPrice': cls._w3.to_wei(21, 'gwei')
    })
    tx_hash = cls._w3.eth.send_transaction(tx)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress
    cls._smart_contract = cls._w3.eth.contract(address=contract_address, abi=abi)
    cls._base = cls._smart_contract.functions.BASE().call()
    print("Smart contract is deployed:", cls._smart_contract.address)
    return cls._smart_contract.address
  
  def __prepare_basics(cls, testnet, port):
    # load environment variables
    load_dotenv()

    # determine test network where to deploy smart contract
    cls._testnet = cls.__determine_testnet(testnet, port)

    # establish web3 connection to the test network
    cls._w3 = Web3(HTTPProvider(cls._testnet, request_kwargs={ 'timeout': 500 }))
    print("Web3 is connected:", cls._w3.is_connected())

    # define default Ganache account for signing
    cls._account = cls._w3.eth.accounts[0]

  def __determine_testnet(cls, testnet, port):
    if testnet == Testnets.KOVAN:
      return 'https://kovan.infura.io/v3/' + os.environ['INFURA_API_KEY']
    elif testnet == Testnets.ROPSTEN:
      return 'https://ropsten.infura.io/v3/' + os.environ['INFURA_API_KEY']
    elif testnet == Testnets.RINKEBY:
      return 'https://rinkeby.infura.io/v3/' + os.environ['INFURA_API_KEY']
    elif testnet == Testnets.GOERLI:
      return 'https://goerli.infura.io/v3/' + os.environ['INFURA_API_KEY']
    elif testnet == Testnets.TRUFFLE:
      return 'http://localhost:9545'
    elif testnet == Testnets.GANACHE:
      return 'http://localhost:' + str(port)
    else:
      raise ValueError('Wrong testnet argument! Arg: ' + str(testnet))

