# built-in libs
import random
import asyncio
import sys
import os
import argparse
import time
import subprocess
import re
import signal
import atexit
from threading import Thread
from queue import Queue
from multiprocessing import Process, current_process
from web3 import Web3, HTTPProvider
# user-defined libs
from chain_msg_handler import ChainHandler
from util import Testnets, MobApps, Settings
from edge_off import EdgeOffloading

# public functions
def cleanup_ganache_processes():
    try:
        output = subprocess.check_output(["ps", "aux"])
        lines = output.decode().splitlines()
        ganache_pids = [line.split()[1] for line in lines if "ganache-cli" in line and "--port" in line]
        for pid in ganache_pids:
            print(f"[CLEANUP] Killing Ganache process PID {pid}")
            os.kill(int(pid), signal.SIGKILL)
    except Exception as e:
        print(f"[ERROR] Cleanup failed: {e}")

def wait_for_ganache_ready(port=8545, min_accounts=1, timeout=10):
    start = time.time()
    w3 = Web3(HTTPProvider(f"http://127.0.0.1:{port}"))
    while time.time() - start < timeout:
        try:
            if w3.is_connected():
                accounts = w3.eth.accounts
                if len(accounts) >= min_accounts:
                    return
        except Exception as e:
            print(e)
        time.sleep(0.3)
    raise RuntimeError(f"Ganache on port {port} failed to return {min_accounts} accounts in time.")

def start_ganache_instance(port):
    mnemonic = ""
    with open("../mnemonic.txt", "r") as mfile:
        mnemonic = mfile.read().strip()
    ganache_cmd = ["ganache-cli", "--port", str(port), "--mnemonic", mnemonic, "--defaultBalanceEther", "1000", "--accounts", "100"]
    proc = subprocess.Popen(ganache_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🚀 Starting Ganache on port {port} with PID {proc.pid}")
    
    import socket
    start = time.time()
    while time.time() - start < 10:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                #break
                return
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
    
    #wait_for_ganache_ready(port = port, min_accounts = 10)

def update_rep_thread (chain, submit_trx):
    t = Thread (target = wrapper_update_rep, args = (chain, submit_trx, ))
    t.start ()

def wrapper_update_rep (chain, submit_trx):
    asyncio.run (update_reputation (chain, submit_trx))

async def update_reputation (chain, submit_trx):
    task = asyncio.create_task(chain.update_reputation(submit_trx))
    task.add_done_callback(lambda future: reputation_update_completed(future, chain))

def reputation_update_completed (future, chain):
    submit_cached_trx (chain)

def submit_cached_trx (chain):
    global update_thread, cached_trx
    submit_trx = list ()

    if cached_trx:
        submit_trx = [trx for trx in cached_trx]
        cached_trx.clear ()
        update_thread = True
        update_rep_thread (chain, submit_trx)
        return

    update_thread = False


def experiment_run (chain):
    # skip real experiment run
    #print("[Mock] experiment_run() called – skipping actual execution.")
    #return
    global req_q, rsp_q, cached_trx, update_thread

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
                submit_cached_trx(chain)
        
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

def run_fresco_sim(alpha, beta, gamma, k, app, suffix, port = 8545):
    """
    Executes full benchmarking across all offloading models (FRESCO, SQ, SMT, MDP)
    with the same application and simulation setup, using legacy-style execution
    and full reputation integration.
    """
    proc_name = current_process().name
    print(f"\n=== Starting {proc_name} ===")
    print(f"[Init] Parameters -> alpha: {alpha}, beta: {beta}, gamma: {gamma}, k: {k}, app: {app}, ID: {suffix}, port: {port}")

    if os.getenv("MULTICHAIN") == "1":
        start_ganache_instance(port)

    handler = ChainHandler(Testnets.GANACHE, port=port, account_index=suffix)
    if not re.fullmatch(r"0x[a-fA-F0-9]{40}", handler._account):
        raise ValueError(f"Invalid Ethereum account for suffix {suffix}: {handler._account}")
    
    if os.getenv("MULTICHAIN") == "1":
        contract_address = handler.deploy_smart_contract()
        handler.load_contract(contract_address)
    else:
        import pathlib
        addr_path = pathlib.Path("contract_address.txt")
        start = time.time()
        while not addr_path.exists():
            if time.time() - start > 10:
                raise RuntimeError("Timeout waiting for contract_address.txt to be created.")
            time.sleep(0.2)
        with open(addr_path, "r") as f:
            addr = f.read().strip()
            handler.load_contract(addr)
    
    edge_off = EdgeOffloading(
        req_q,
        rsp_q,
        Settings.APP_EXECUTIONS,
        Settings.SAMPLES,
        app,
        Settings.CONSENSUS_DELAY,
        Settings.SCALABILITY,
        Settings.NUM_LOCS,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        k=k,
        suffix=suffix,
        disable_trace_log=True
    )

    edge_off.deploy_fresco_ode()
    edge_off._id_suffix = suffix
    edge_off.start()
    experiment_run(handler)
    output_filename = f"fresco_sensitivity/results_fresco_a{alpha}_b{beta}_k{k}_s{suffix}.csv"
    edge_off.log_sensitivity_summary(output_filename)
    print(f"[{proc_name}] Summary saved to {output_filename}")

atexit.register(cleanup_ganache_processes)
signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
random.seed (42)
# public variables
reg_nodes = list ()
cached_trx = list ()
update_thread = False
req_q, rsp_q = Queue (), Queue ()
#chain = None

#if (len (sys.argv) - 1) == 2: 
#  chain = ChainHandler (Testnets.GANACHE, port = sys.argv[2], account_index = 0)
#else:
#  chain = ChainHandler (Testnets.GANACHE, account_index = 0)

# contract_address = chain.deploy_smart_contract ()
#with open("contract_address.txt", "w") as f:
#    f.write(contract_address)

if sys.argv[1] == 'intra':
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
        MobApps.INTRASAFED, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_fresco_ode ()
    edge_off.start ()

    experiment_run ()
    
    edge_off = EdgeOffloading (req_q, rsp_q, Settings.APP_EXECUTIONS, Settings.SAMPLES, \
       MobApps.INTRASAFED, Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS)
    edge_off.deploy_sq_ode ()
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fresco_sweep", "intra", "mobiar", "naviar"])
    parser.add_argument("--multi-chain", action="store_true")
    args = parser.parse_args()

    if not args.multi_chain:
        start_ganache_instance(8545)

        # Deploy contract if not already done
        deployer = ChainHandler(Testnets.GANACHE, account_index=0)
        contract_address = deployer.deploy_smart_contract()
        with open("contract_address.txt", "w") as f:
            f.write(contract_address)

    if args.mode == 'fresco_sweep':
        app = MobApps.INTRASAFED
        alphas = [0.2, 0.4, 0.6]
        betas = [0.2, 0.4]
        k = 5
        processes = []
        suffix = 1
        base_port = 8545
        
        if args.multi_chain:
            os.environ["MULTICHAIN"] = "1"

        for alpha in alphas:
            for beta in betas:
                gamma = 1.0 - alpha - beta
                if gamma < 0:
                    continue
            
                port = (base_port + suffix) if args.multi_chain else 8545
                proc = Process(target=run_fresco_sim, args=(alpha, beta, gamma, k, app, suffix), kwargs={"port": port})
                proc.start()
                processes.append(proc)
                suffix += 1

        for proc in processes:
            proc.join()
        
        cleanup_ganache_processes()
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
