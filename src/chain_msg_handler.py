# built-in libs
import os
import json

# third-party libs
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.exceptions import ContractLogicError

# user-defined libs
from util import Testnets, PrivateKeys


class ChainHandler:
    def __init__(self, testnet, port = 8545, account_index = 0):
        self._abi_file_path = "../build/contracts/Reputation.json"
        self._w3 = None
        self._testnet = None
        self._smart_contract = None
        self._account = None
        self._base = None
        self._contract_address = None
        self._account_index = account_index
        self.__prepare_basics(testnet, port)

    def __prepare_basics(self, testnet, port):
        load_dotenv()
        self._testnet = self.__determine_testnet(testnet, port)
        #print(self._testnet)
        self._w3 = Web3(HTTPProvider(self._testnet, request_kwargs={'timeout': 500}))
        self._account = self._w3.eth.accounts[self._account_index]
        print(f"Web3 is connected: {self._w3.is_connected()}; [Proc {self._account_index}] Using account: {self._account}")

    def __determine_testnet(self, testnet, port):
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

    def load_contract(self, contract_address):
        self._contract_address = contract_address
        with open(self._abi_file_path, 'r') as abi_file:
            abi_json = json.load(abi_file)
            abi = abi_json['abi']
        self._smart_contract = self._w3.eth.contract(address=contract_address, abi=abi)
        self._base = self._smart_contract.functions.BASE().call()

    def deploy_smart_contract(self):
        with open(self._abi_file_path, 'r') as f:
            truffle_file = json.load(f)
        abi = truffle_file['abi']
        bytecode = truffle_file['bytecode']
        contract_factory = self._w3.eth.contract(abi=abi, bytecode=bytecode)

        tx = contract_factory.constructor().build_transaction({
            'from': self._account,
            'nonce': self._w3.eth.get_transaction_count(self._account),
            'gas': 1728712,
            'gasPrice': self._w3.to_wei(21, 'gwei')
        })
        tx_hash = self._w3.eth.send_transaction(tx)
        tx_receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)

        self._smart_contract = self._w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        self._base = self._smart_contract.functions.BASE().call()
        print("Smart contract is deployed:", self._smart_contract.address)
        return self._smart_contract.address

    def get_base(self):
        return self._smart_contract.functions.BASE().call()

    def get_reputation(self, nodeId):
        try:
            return self._smart_contract.functions.getReputationScore(nodeId).call()[0] / self._base
        except ContractLogicError as e:
            print("Contract logic error occurred:", str(e))
            return None

    def register_node(self, nodeId):
        event = self._smart_contract.events.NodeRegistered()
        nonce = self._w3.eth.get_transaction_count(self._account)
        #print(f"[{self._account}] Using nonce = {nonce}")
        tx = self._smart_contract.functions.registerNode(nodeId).build_transaction({
            'from': self._account,
            'gasPrice': self._w3.eth.gas_price,
            'nonce': nonce
        })
        tx_hash = self._w3.eth.send_transaction(tx)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return event.process_receipt(receipt)[0]['args']

    def unregister_node(self, nodeId):
        event = self._smart_contract.events.NodeUnregistered()
        tx = self._smart_contract.functions.unregisterNode(nodeId).build_transaction({
            'from': self._account,
            'gasPrice': self._w3.eth.gas_price,
            'nonce': self._w3.eth.get_transaction_count(self._account)
        })
        tx_hash = self._w3.eth.send_transaction(tx)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return event.process_receipt(receipt)[0]['args']

    async def update_reputation(self, transactions):
        event = self._smart_contract.events.ReputationUpdate()
        tx = self._smart_contract.functions.updateNodeReputation(transactions).build_transaction({
            'from': self._account,
            'gasPrice': self._w3.eth.gas_price,
            'nonce': self._w3.eth.get_transaction_count(self._account)
        })
        tx_hash = self._w3.eth.send_transaction(tx)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        result = event.process_receipt(receipt)[0]['args']

        return [{'id': r.id, 'score': r.value / self._base} for r in result.rsp]

    def reset_reputation(self, ids):
        event = self._smart_contract.events.ResetReputation()
        tx = self._smart_contract.functions.resetReputations(ids).build_transaction({
            'from': self._account,
            'gasPrice': self._w3.eth.gas_price,
            'nonce': self._w3.eth.get_transaction_count(self._account)
        })
        tx_hash = self._w3.eth.send_transaction(tx)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        result = event.process_receipt(receipt)[0]['args']

        return [{'id': r.id, 'score': r.value / self._base} for r in result.rsp]

