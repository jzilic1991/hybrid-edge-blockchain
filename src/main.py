# built-in libs
import random
import asyncio
from flask import Flask, request, jsonify
from threading import Thread

# user-defined libs
from chain_msg_handler import ChainMsgHandler
from util import Testnets


# public variables
cluster_nodes = list ()
update_rep_finished = True
cached_transaction_pool = tuple ()


# public functions
# def register_nodes (chain):
#     nodes = list ()

#     nodes.append (chain.register_node ('Node A'))
#     nodes.append (chain.register_node ('Node B'))

#     return nodes


# def init_rep_scores (chain, nodes):
#     for i in range (2):
#         chain.update_reputation_score (nodes[0], int(round(random.uniform (-1, 1), 3) * 1000))

#     for i in range (2):
#         chain.update_reputation_score (nodes[1], int(round(random.uniform (-1, 1), 3) * 1000))

# general-purpose public functions
def start_update_reputation_thread ():
    
    t2 = Thread(target = wrapper_update_reputation, args = (cached_transaction_pool,))
    t2.start ()

    cached_transaction_pool = tuple ()



# callback functions
def reputation_update_completed (future):

    update_rep_finished = True
    print ('Reputation is update for following nodes: ' + str (future.result ()))

    if len (cached_transaction_pool):
        start_update_reputation_thread ()


def deploy_sc_task_completed (future):

    print ('Smart contract is deployed on address: ' + str (future.result ()))


def node_registration_completed (future):

    cluster_nodes.append (future.result ())
    print ('Node is registered: ' + str (future.result ()))




# asynchornous functions
async def deploy_smart_contract (chain):
    
    task = asyncio.create_task (chain.deploy_smart_contract ())
    task.add_done_callback (deploy_sc_task_completed)


async def update_reputation (transactions):
    
    task = asyncio.create_task (chain.update_reputation_score (transactions))
    task.add_done_callback (reputation_update_completed)


async def node_registration (name):
    
    task = asyncio.create_task (chain.register_node (name))
    task.add_done_callback (node_registration_completed)




# wrapper functions for async functions
def wrapper_deploy_sc (chain):

    asyncio.run (deploy_smart_contract (chain))


def wrapper_update_reputation (transactions):

    update_rep_finished = False
    asyncio.run (update_reputation (transactions))


def wrapper_node_registration (name):
    
    asyncio.run (node_registration (name))




# blockchain handler instantiation
chain = ChainMsgHandler (Testnets.ROPSTEN)

# thread smart contract deployment
t1 = Thread(target = wrapper_deploy_sc, args = (chain,))
t1.start ()

# web server instantiation
app = Flask(__name__)




# web server API functions
@app.route('/update')
def update_reputation_score ():

    nodeid = int (request.args.get('id', None))
    reward = float (request.args.get('reward', None))

    cached_transaction_pool += ({ 'id': nodeid, 'reward': reward })

    if update_rep_finished:
        start_update_reputation_thread ()
        
    return jsonify ()


@app.route('/register')
def register_node ():

    name = str (request.args.get('name', None))

    while t1.is_alive ():
        continue

    t3 = Thread(target = wrapper_node_registration, args = (name,))
    t3.start ()

    while t3.is_alive ():
        continue

    return jsonify ('Node registration status: ' + cluster_nodes[-1])


@app.route('/get_rep')
def get_reputation_score ():

    nodeid = int (request.args.get('id', None))

    for ele in cluster_nodes:
        if ele['id'] == nodeid:
            return jsonify (chain.get_reputation_score (nodeid))

    return jsonify (float ('nan'))




# main entrypoint and web server start-up
if __name__ == "__main__":

    app.run(host = '0.0.0.0', port = 5000, debug = True, use_reloader = False)