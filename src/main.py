# built-in libs
import random
import asyncio
from threading import Thread
from queue import Queue

# user-defined libs
from chain_msg_handler import ChainHandler
from util import Testnets
from main_smt import EdgeOffloading


# public functions
def update_rep_thread (chain, submit_trx):
    
    print ('MAIN THREAD - Submitted transactions: ' + str (submit_trx))
    t = Thread (target = wrapper_update_rep, args = (chain, submit_trx, ))
    t.start ()


def wrapper_update_rep (chain, submit_trx):

    asyncio.run (update_reputation (chain, submit_trx))


async def update_reputation (chain, submit_trx):
    
    task = asyncio.create_task (chain.update_reputation (submit_trx))
    task.add_done_callback (reputation_update_completed)


def reputation_update_completed (future):

    print ("MAIN THREAD - Reputation score update: " + str (future.result ()))
    submit_cached_trx ()


def submit_cached_trx ():

    global update_thread, cached_trx
    submit_trx = list ()

    if cached_trx:

        submit_trx = [trx for trx in cached_trx]
        cached_trx.clear ()
        update_thread = True
        update_rep_thread (chain, submit_trx)
        return

    update_thread = False


# public variables
reg_nodes = list ()
cached_trx = list ()
update_thread = False
req_q, rsp_q = Queue (), Queue ()

chain = ChainHandler (Testnets.TRUFFLE)
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

        print ("MAIN THREAD - Received offloading transaction: " + str (msg[1]))

        if update_thread:

            for trx in msg[1]:
                
                cached_trx.append (trx)

            print ("Cached offloading transactions: " + str (cached_trx))
        
        else:

            cached_trx += [trx for trx in msg[1]]
            submit_cached_trx ()

    elif msg[0] == 'get':

        site_rep = []
        for n_id in msg[1]: 
            
            site_rep.append((n_id, chain.get_reputation (n_id)))

        rsp_q.put (('get_rsp', site_rep))

    elif msg == 'close':

        rsp_q.put ('confirm')
        print ('MAIN THREAD is done.')
        break
