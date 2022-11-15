# built-in libs
import random
import asyncio
from threading import Thread

# user-defined libs
from chain_msg_handler import ChainMsgHandler
from util import Testnets




# public variables
cluster_nodes = list ()
update_rep_finished = True
cached_transaction_pool = list ()
chain = ChainMsgHandler (Testnets.GANACHE)


# public functions
def start_update_reputation_thread ():
    
    print ('Submitted transaction pool: ' + str (cached_transaction_pool))
    t2 = Thread(target = wrapper_update_reputation)
    t2.start ()


def register_nodes ():
    
    names = ("MD1", "EC1", "ED1", "ER1", "CD1")

    t3 = Thread(target = wrapper_node_registration, args = (names[0],))
    t4 = Thread(target = wrapper_node_registration, args = (names[1],))

    for name in names:
        
        t = Thread(target = wrapper_node_registration, args = (name,))
        t.start ()

        while t.is_alive ():

            continue



def update_rep_scores ():
    
    for node in cluster_nodes:
        for i in range (2):
            cached_transaction_pool.append ([node['id'], int(round(random.uniform (0, 1), 3) * 1000)])

    start_update_reputation_thread ()
    




# callback functions
def reputation_update_completed (future):

    print ("Reputation score update: " + str (future.result ()))
    
    cached_transaction_pool.clear ()
    update_rep_finished = True
    update_rep_scores ()


def deploy_sc_task_completed (future):

    print ('Smart contract is deployed on address: ' + str (future.result ()))


def node_registration_completed (future):

    cluster_nodes.append (future.result ())
    print ('Node is registered: ' + str (future.result ()))




# asynchornous functions
async def deploy_smart_contract ():
    
    task = asyncio.create_task (chain.deploy_smart_contract ())
    task.add_done_callback (deploy_sc_task_completed)


async def update_reputation ():
    
    task = asyncio.create_task (chain.update_reputation_score (cached_transaction_pool))
    task.add_done_callback (reputation_update_completed)


async def node_registration (name):
    
    task = asyncio.create_task (chain.register_node (name))
    task.add_done_callback (node_registration_completed)




# wrapper functions for async functions
def wrapper_deploy_sc ():

    asyncio.run (deploy_smart_contract ())


def wrapper_update_reputation ():

    update_rep_finished = False
    asyncio.run (update_reputation ())


def wrapper_node_registration (name):
    
    asyncio.run (node_registration (name))




# thread smart contract deployment
t1 = Thread(target = wrapper_deploy_sc)
t1.start ()

while t1.is_alive ():
    
    continue  

register_nodes ()
update_rep_scores ()