# built-in libs
import random
import asyncio
from threading import Thread
from queue import Queue

# user-defined libs
from chain_msg_handler import ChainMsgHandler
from util import Testnets
from main_smt import EdgeOffloading


# public functions
def update_rep_thread (chain, off_transaction):
    
    print ('MAIN THREAD - Submitted transaction: ' + str (off_transaction))
    t = Thread (target = wrapper_update_rep, args = (chain, off_transaction, ))
    t.start ()


def wrapper_update_rep (chain, off_transaction):

    asyncio.run (update_reputation (chain, off_transaction))


async def update_reputation (chain, off_transaction):
    
    task = asyncio.create_task (chain.update_reputation (off_transaction))
    task.add_done_callback (reputation_update_completed)


def reputation_update_completed (future):

    print ("MAIN THREAD - Reputation score update: " + str (future.result ()))


# public variables
reg_nodes = list ()
req_q, rsp_q = Queue (), Queue ()
chain = ChainMsgHandler (Testnets.TRUFFLE)
chain.deploy_smart_contract ()
edge_off = EdgeOffloading (req_q, rsp_q)
edge_off.start ()

# node registration
msg = req_q.get ()
if msg[0] == 'reg':

    for name in msg[1]:

        result = chain.register_node (name)
        # print ('Node is registered: ' + str (result))
        reg_nodes.append (result)

rsp_q.put (('reg_rsp', reg_nodes))

while True:

    msg = req_q.get ()

    if msg[0] == 'update':

        update_rep_thread (chain, [[msg[1], msg[2]]])

    elif msg[0] == 'get':

        site_rep = []
        for n_id in msg[1]: 
            
            site_rep.append((n_id, chain.get_reputation (n_id)))

        rsp_q.put (('get_rsp', site_rep))
