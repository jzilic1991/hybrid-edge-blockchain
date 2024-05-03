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
      print ("Contract logic error occured: " + e)
      return None


  def register_node (cls, nodeId):

    registration_event = cls._smart_contract.events.NodeRegistered ()
    tx = cls._smart_contract.functions.registerNode(nodeId).build_transaction({
            'from': cls._account.address,
            'gasPrice': cls._w3.eth.gas_price,
            'nonce': cls._w3.eth.get_transaction_count (cls._account.address)
        })

    signed_tx = cls._w3.eth.account.sign_transaction (tx, cls._key)
    tx_hash = cls._w3.eth.send_raw_transaction (signed_tx.rawTransaction)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt (tx_hash)
    result = registration_event.process_receipt(tx_receipt)
    # print ("Node registration event: " + str (result))

    return result[0]['args']


  def unregister_node (cls, nodeId):

    registration_event = cls._smart_contract.events.NodeUnregistered ()
    tx = cls._smart_contract.functions.unregisterNode(nodeId).build_transaction({
            'from': cls._account.address,
            'gasPrice': cls._w3.eth.gas_price,
            'nonce': cls._w3.eth.get_transaction_count (cls._account.address)
        })

    signed_tx = cls._w3.eth.account.sign_transaction (tx, cls._key)
    tx_hash = cls._w3.eth.send_raw_transaction (signed_tx.rawTransaction)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt (tx_hash)
    result = registration_event.process_receipt(tx_receipt)

    return result[0]['args']


  async def update_reputation (cls, transactions):

    # print ('Incentive: ' + str (incentive / cls._base))
    reputation_update_event = cls._smart_contract.events.ReputationUpdate ()
    tx = cls._smart_contract.functions.updateNodeReputation(transactions).build_transaction({
            'from': cls._account.address,
            'gasPrice': cls._w3.eth.gas_price,
            'nonce': cls._w3.eth.get_transaction_count (cls._account.address)
        })
    
    signed_tx = cls._w3.eth.account.sign_transaction (tx, cls._key)
    # start = time.time ()
    tx_hash = cls._w3.eth.send_raw_transaction (signed_tx.rawTransaction)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt (tx_hash)
    result = reputation_update_event.process_receipt(tx_receipt)
    # end = time.time ()
    event = result[0]['args']
    # print ("Update reputation event: " + str (result))
    response = list ()
    for i in range (len (event.rsp)):
      response.append ({ 'id': event.rsp[i].id, 'score': event.rsp[i].value / cls._base })
    # print ('Elapsed time is ' + str (round (end - start, 3)) + ' s')
    return (response)


  def reset_reputation (cls, ids):

    # print ('Incentive: ' + str (incentive / cls._base))
    reset_event = cls._smart_contract.events.ResetReputation ()
    tx = cls._smart_contract.functions.resetReputations(ids).build_transaction({
            'from': cls._account.address,
            'gasPrice': cls._w3.eth.gas_price,
            'nonce': cls._w3.eth.get_transaction_count (cls._account.address)
        })

    signed_tx = cls._w3.eth.account.sign_transaction (tx, cls._key)
    # start = time.time ()
    tx_hash = cls._w3.eth.send_raw_transaction (signed_tx.rawTransaction)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt (tx_hash)
    result = reset_event.process_receipt(tx_receipt)
    # end = time.time ()
    event = result[0]['args']
    response = list ()
    for i in range (len (event.rsp)):
      response.append ({ 'id': event.rsp[i].id, 'score': event.rsp[i].value / cls._base })

    # print ('Elapsed time is ' + str (round (end - start, 3)) + ' s')
    return (response)


  def deploy_smart_contract (cls):
    
    # load smart contract data structure
    truffle_file = json.load (open ('.././build/contracts/Reputation.json'))
    abi = truffle_file['abi']
    bytecode = truffle_file['bytecode']
    cls._smart_contract = cls._w3.eth.contract (bytecode = bytecode, abi = abi)

    # deploy smart contract instance
    tx = cls._smart_contract.constructor().build_transaction({ 
          'from': cls._account.address, 
          'nonce': cls._w3.eth.get_transaction_count (cls._account.address),
          'gas': 1728712,
          'gasPrice': cls._w3.to_wei (21, 'gwei')
      })
  
    signed_tx = cls._account.sign_transaction (tx)
    tx_hash = cls._w3.eth.send_raw_transaction (signed_tx.rawTransaction)
    tx_receipt = cls._w3.eth.wait_for_transaction_receipt (tx_hash)
    contract_address = tx_receipt.contractAddress
    cls._smart_contract = cls._w3.eth.contract (address = contract_address, abi = abi)
    cls._base = cls._smart_contract.functions.BASE().call()
    print ("Smart contract is deployed: " + str(cls._smart_contract.address))

    return cls._smart_contract.address


  def __prepare_basics (cls, testnet, port):

    # load environment variables
    load_dotenv()

    # determine test network where to deploy smart contract
    cls._testnet = cls.__determine_testnet (testnet, port)

    # establish web3 connection to the test network
    cls._w3 = Web3 (HTTPProvider (cls._testnet, request_kwargs = { 'timeout': 30 }))
    print ("Web3 is connected: " + str(cls._w3.is_connected ()))

    # determine private key and user account
    cls._key = cls.__determine_private_key(testnet)
    cls._account = cls._w3.eth.account.from_key (cls._key)


  def __determine_testnet (cls, testnet, port):

    # determine a test network for deploying the smart contract
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
      return 'http://localhost:' + str (port)

    else:
      raise ValueError ('Wrong testnet argument! Arg: ' + str (testnet))


  def __determine_private_key (cls, testnet):

    # determine a user account based on a private key
    if testnet == Testnets.KOVAN or testnet == Testnets.ROPSTEN or testnet == Testnets.RINKEBY:
      return os.environ['PRIVATE_KEY']

    elif testnet == Testnets.TRUFFLE:
      return PrivateKeys.TRUFFLE

    elif testnet == Testnets.GANACHE:
      return PrivateKeys.GANACHE
