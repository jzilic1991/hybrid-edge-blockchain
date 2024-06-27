# built-in libs
import random
import asyncio
import sys
from threading import Thread
from queue import Queue

# user-defined libs
from chain_msg_handler import ChainHandler
from util import Testnets, MobApps, Settings
from edge_off import EdgeOffloading



# public functions
def update_rep_thread (chain, submit_trx):
    
    t = Thread (target = wrapper_update_rep, args = (chain, submit_trx, ))
    t.start ()


def wrapper_update_rep (chain, submit_trx):

    asyncio.run (update_reputation (chain, submit_trx))


async def update_reputation (chain, submit_trx):
    
    task = asyncio.create_task (chain.update_reputation (submit_trx))
    task.add_done_callback (reputation_update_completed)


def reputation_update_completed (future):

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


def experiment_run ():

    global chain, req_q, rsp_q, cached_trx, update_thread

    while True:
        # node registration
        msg = req_q.get ()
        if msg[0] == 'reg':
            for name in msg[1]:
                result = chain.register_node (name)
                # print ('Node is registered: ' + str (result))
                reg_nodes.append (result)

            rsp_q.put (('reg_rsp', reg_nodes))

        # offloading transactions
        elif msg[0] == 'update':
            if update_thread:
                for trx in msg[1]:
                        cached_trx.append (trx)
            else:
                cached_trx += [trx for trx in msg[1]]
                submit_cached_trx ()
        
        # get reputation per offloading site
        elif msg[0] == 'get':
            site_rep = []
            for n_id in msg[1]: 
                site_rep.append((n_id, chain.get_reputation (n_id)))

            rsp_q.put (('get_rsp', site_rep))
        
        # reset reputation
        elif msg[0] == 'reset':
            while True:
                if not update_thread:
                    rsp_q.put (('reset_rsp', chain.reset_reputation (msg[1])))
                    break
        
        # unregister node
        elif msg[0] == 'close':
            for nodeId in msg[1]:
                while True:
                    if not update_thread:
                        result = chain.unregister_node (nodeId)
                        break
                    
                    # print ('Node is unregistered: ' + str (result))
            
            rsp_q.put ('confirm')
            break
        
        # wrong or unknown message is received
        else:

          raise ValueError ("Wrong message received from offloading thread: " + str (msg[0]))


random.seed (42)
# public variables
reg_nodes = list ()
cached_trx = list ()
update_thread = False
req_q, rsp_q = Queue (), Queue ()
chain = None

if (len (sys.argv) - 1) == 2: 
  chain = ChainHandler (Testnets.GANACHE, sys.argv[2])
else:
  chain = ChainHandler (Testnets.GANACHE)

chain.deploy_smart_contract ()

if sys.argv[1] == 'intra':
    
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
       MobApps.INTRASAFED, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_sq_ode ()
    edge_off.start ()

    experiment_run ()
    exit ()    
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.INTRASAFED, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_fresco_ode ()
    edge_off.start ()

    experiment_run ()
    
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.INTRASAFED, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_smt_ode ()
    edge_off.start ()

    experiment_run ()
    
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.INTRASAFED, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_mdp_ode ()
    edge_off.start ()

    experiment_run ()


elif sys.argv[1] == 'mobiar':

    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.MOBIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_sq_ode ()
    edge_off.start ()

    experiment_run ()
    exit ()
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.MOBIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_fresco_ode ()
    edge_off.start ()

    experiment_run ()
        
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.MOBIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_smt_ode ()
    edge_off.start ()

    experiment_run ()
    
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.MOBIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_mdp_ode ()
    edge_off.start ()

    experiment_run ()

if sys.argv[1] == 'naviar':
   
   edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.NAVIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
   edge_off.deploy_sq_ode ()
   edge_off.start ()

   experiment_run ()
   exit ()
   edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
       MobApps.NAVIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
   edge_off.deploy_fresco_ode ()
   edge_off.start ()

   experiment_run ()
    
   edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
       MobApps.NAVIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
   edge_off.deploy_mdp_ode ()
   edge_off.start ()

   experiment_run ()
    
   # for i in [2,4,8,16,32]:
   edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
       MobApps.NAVIAR, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
   edge_off.deploy_smt_ode ()
   edge_off.start ()

   experiment_run ()
    

   #  # for i in [1, 5, 10, 15, 30, 50, 80, 100]:



# edge_off = EdgeOffloading (req_q, rsp_q, 100, 2)
# edge_off.deploy_sq_ode ()
# edge_off.start ()

# experiment_run ()

# edge_off = EdgeOffloading (req_q, rsp_q, 100, 2)
# edge_off.deploy_rep_smt_ode ()
# edge_off.start ()

# experiment_run ()

# edge_off = EdgeOffloading (req_q, rsp_q, 100, 2)
# edge_off.deploy_smt_ode ()
# edge_off.start ()

# experiment_run ()
