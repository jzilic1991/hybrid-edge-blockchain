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
import multiprocessing
import socket
import shutil
import logging
import tempfile
from datetime import datetime
from threading import Thread
from queue import Queue
from multiprocessing import Process, current_process, Event
from web3 import Web3, HTTPProvider
# user-defined libs
from chain_msg_handler import ChainHandler
from util import Testnets, MobApps, Settings
from edge_off import EdgeOffloading
from logging_setup import setup_logging

logger = logging.getLogger(__name__)
setup_logging(os.path.join("logs", "simulation.log"))
# Will be set to the PID of the main process inside the
# ``if __name__ == "__main__"`` block. Child processes keep this
# value to identify that they are not the main process.
MAIN_PID = None
# Track Ganache processes started by this instance so we only
# terminate our own at cleanup time.
GANACHE_PROCESSES = []

def handle_interrupt(signum, frame):
    logger.info(f"\n[INTERRUPT] Received signal {signum}. Cleaning up...")

    for child in multiprocessing.active_children():
        logger.info(f"[CLEANUP] Terminating child PID={child.pid}")
        child.terminate()
        child.join(timeout=5)

    cleanup_ganache_processes()
    sys.exit(1)

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = log_uncaught_exceptions

def init_sensitivity_csvs():
    results_dir = "fresco_sensitivity/"
    os.makedirs(results_dir, exist_ok=True)

    for app in ["mobiar", "intrasafe", "naviar", "random"]:
        filepath = os.path.join(results_dir, f"{app}.csv")
        with open(filepath, "w") as f:
            f.write(
                "suffix,alpha,beta,gamma,k,latency,energy,cost,dec_time,qos_violation,ER,EC,ED,MD,CD,score\n"
            )

def find_available_port(starting_from, used_ports):
    port = starting_from
    while port < 65535:
        if port in used_ports:
            port += 1
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                used_ports.add(port)
                return port
        port += 1
    raise RuntimeError("No available ports found.")

def cleanup_ganache_processes(proc=None, tmp_erase=True):
    """Terminate Ganache processes started by this instance."""
    global GANACHE_PROCESSES

    targets = []
    if proc is not None:
      targets = [entry for entry in GANACHE_PROCESSES if entry[0] == proc]
    else:
      targets = GANACHE_PROCESSES[:]
    for p, tdir in targets:
        try:
          if p.poll() is None:
                logger.info(f"[CLEANUP] Terminating Ganache subprocess PID={p.pid}")
                p.terminate()
                p.wait(timeout=3)
        except Exception as e:
          logger.warning(f"[CLEANUP] Failed to terminate Ganache: {e}")

        if tmp_erase and tdir:
            clean_ganache_temp([tdir])

        if (p, tdir) in GANACHE_PROCESSES:
            GANACHE_PROCESSES.remove((p, tdir))

def clean_ganache_temp(dirs=None):
    """Remove Ganache temporary directories for this instance."""
    logger.info("[INFO] Cleaning old Ganache temp files in /tmp...")
    import glob
    
    if dirs is None:
        dirs = glob.glob("/tmp/tmp-*")

    for temp_path in dirs:
        try:
            if os.path.isdir(temp_path):
                shutil.rmtree(temp_path)
            else:
                os.remove(temp_path)
            logger.info(f"[CLEANUP] Removed {temp_path}")
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.info(f"[WARN] Could not delete {temp_path}: {e}")

def start_ganache_instance(port):
    mnemonic = ""
    with open("../mnemonic.txt", "r") as mfile:
        mnemonic = mfile.read().strip()
    os.makedirs("ganache_logs", exist_ok=True)
    logfile_path = f"ganache_logs/ganache_{port}.log"
    logfile = open(logfile_path, "w")
    temp_dir = tempfile.mkdtemp(prefix=f"ganache_{port}_")
    ganache_cmd = [
        "ganache-cli",
        "--port", str(port),
        "--mnemonic", mnemonic,
        "--defaultBalanceEther", "1000",
        "--accounts", "100",
        "--db", temp_dir
    ]

    try:
        proc = subprocess.Popen(ganache_cmd, stdout=logfile, stderr=subprocess.STDOUT)
        GANACHE_PROCESSES.append((proc, temp_dir))
    finally:
        logfile.close()

    logger.info(
        f"🚀 Starting Ganache on port {port} with PID {proc.pid}, logging to {logfile_path}"
    )

    start = time.time()
    while time.time() - start < 10:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return proc
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
    

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


def experiment_run (chain, req_q, rsp_q):
    # skip real experiment run
    #print("[Mock] experiment_run() called – skipping actual execution.")
    #return
    global cached_trx, update_thread

    while True:
        # node registration
        msg = req_q.get ()
        if msg[0] == 'reg':
            for name in msg[1]:
                result = chain.register_node (name)
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
            
            rsp_q.put ('confirm')
            break
        
        # wrong or unknown message is received
        else:
          raise ValueError ("Wrong message received from offloading thread: " + str (msg[0]))


def run_qrl_sim(app, suffix, profile, port=8545):
    """Run simulation using the QRL offloading decision engine."""

    req_q, rsp_q = Queue(), Queue()
    proc_name = current_process().name
    print(f"\n=== Starting {proc_name} ===")
    print(f"[Init] Parameters -> app: {app}, ID: {suffix}, port: {port}")
    Settings.workload_profile = profile
    print(f"[SETTINGS] Workload profile set to: {Settings.workload_profile}")
    
    stop_event = Event()
    edge_off = EdgeOffloading(
        req_q,
        rsp_q,
        Settings.APP_EXECUTIONS,
        Settings.SAMPLES,
        Settings.CONSENSUS_DELAY,
        Settings.SCALABILITY,
        Settings.NUM_LOCS,
        suffix=suffix,
        app_name=app,
        profile=profile,
        disable_trace_log = False,
        stop_event = stop_event
    )

    edge_off.deploy_qrl_ode()
    edge_off._id_suffix = suffix
    edge_off.start()
    try:
        edge_off.join()
    except KeyboardInterrupt:
        logger.warning(f"[INTERRUPT] Simulation interrupted. Stopping EdgeOffloading...")
        stop_event.set()  # ✅ signal the thread to shut down
        edge_off.join(timeout=5)
        if edge_off.is_alive():
            logger.error(f"[FORCE] EdgeOffloading thread did not exit cleanly.")
    finally:
      cleanup_child_processes(edge_off)

def run_fresco_sim(alpha, beta, gamma, k, app, suffix, profile, port=8545, sweep=False):
    """
    Executes full benchmarking across all offloading models (FRESCO, SQ, SMT, MDP)
    with the same application and simulation setup, using legacy-style execution
    and full reputation integration.
    """
    req_q, rsp_q = Queue(), Queue()
    proc_name = current_process().name
    logger.info(f"\n=== Starting {proc_name} ===")
    logger.info(f"[Init] Parameters -> α={alpha}, β={beta}, γ={gamma}, k={k}, app={app}, ID={suffix}, port={port}")
    Settings.workload_profile = profile
    logger.info(f"[SETTINGS] Workload profile set to: {Settings.workload_profile}")
    
    ganache_proc = None
    edge_off = None
    stop_event = Event()

    #if os.getenv("MULTICHAIN") == "1":
    #    ganache_proc = start_ganache_instance(port)

    try:
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
                handler.load_contract(f.read().strip())

        edge_off = EdgeOffloading(
            req_q, rsp_q,
            Settings.APP_EXECUTIONS, Settings.SAMPLES,
            Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS,
            alpha=alpha, beta=beta, gamma=gamma, k=k,
            suffix=suffix, app_name=app, profile=profile,
            disable_trace_log=False, use_blockchain=True,
            stop_event=stop_event
        )

        edge_off.deploy_fresco_ode()
        edge_off._id_suffix = suffix
        edge_off.start()
        experiment_run(handler, req_q, rsp_q)
        
        if sweep:
            edge_off.log_sensitivity_summary()
            logger.info(f"[{proc_name}] Summary saved for α={alpha}, β={beta}, γ={gamma}")

    except Exception as e:
        logger.exception(f"[{proc_name}] Exception occurred: {e}")
    finally:
        logger.info(f"[{proc_name}] Entering final cleanup...")
        cleanup_child_processes(edge_off)
        logger.info(f"[{proc_name}] Final cleanup complete.")

def run_simulation(ode_type, app, suffix, profile, port=8545):
    """
    Unified simulation runner for SQ, SMT, MDP, QRL (FRESCO uses run_fresco_sim separately).
    Automatically skips blockchain setup if not needed.
    """
    req_q, rsp_q = Queue(), Queue()
    proc_name = current_process().name
    logger.info(f"\n=== Starting {proc_name} - {ode_type.upper()} ===")
    logger.info(f"[Init] app={app}, suffix={suffix}, port={port}, model={ode_type}")

    use_blockchain = ode_type in ("fresco", "sq")
    ganache_proc = None
    edge_off = None

    #if use_blockchain and os.getenv("MULTICHAIN") == "1":
    #    ganache_proc = start_ganache_instance(port)

    try:
        handler = None
        if use_blockchain:
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

        stop_event = Event()
        edge_off = EdgeOffloading(
            req_q, rsp_q,
            Settings.APP_EXECUTIONS, Settings.SAMPLES,
            Settings.CONSENSUS_DELAY, Settings.SCALABILITY, Settings.NUM_LOCS,
            suffix=suffix, app_name=app, profile=profile, disable_trace_log=False, 
            use_blockchain = use_blockchain, stop_event = stop_event
        )

        deploy_map = {
            "sq": edge_off.deploy_sq_ode,
            "smt": edge_off.deploy_smt_ode,
            "mdp": edge_off.deploy_mdp_ode,
            "qrl": edge_off.deploy_qrl_ode,
        }

        if ode_type not in deploy_map:
            raise ValueError(f"Unsupported model: {ode_type}")

        deploy_map[ode_type]()  # Dynamically invoke deployment method

        edge_off._id_suffix = suffix
        edge_off.start()

        if use_blockchain:
            experiment_run(handler, req_q, rsp_q)
        else:
            # No blockchain run loop needed
            try:
                edge_off.join()
            except KeyboardInterrupt:
                logger.warning(f"[INTERRUPT] Simulation interrupted. Stopping EdgeOffloading...")
                stop_event.set()  # ✅ signal the thread to shut down
                edge_off.join(timeout=5)
                if edge_off.is_alive():
                    logger.error(f"[FORCE] EdgeOffloading thread did not exit cleanly.")

    finally:
        cleanup_child_processes(edge_off)

def cleanup_child_processes(edge_off):
    logger.info("[CLEANUP] Running child process/thread cleanup")

    children = multiprocessing.active_children()
    if not children:
        logger.info("[CLEANUP] No active multiprocessing children detected.")
    else:
        logger.info(f"[CLEANUP] Found {len(children)} active child processes:")
        for child in children:
            logger.info(f" - PID={child.pid} Name={child.name} Alive={child.is_alive()}")

    for child in children:
        try:
            logger.info(f"[CLEANUP] Terminating child process PID={child.pid}")
            child.terminate()
            child.join(timeout=5)
            logger.info(f"[CLEANUP] Child process PID={child.pid} terminated")
        except Exception as e:
            logger.error(f"[CLEANUP] Failed to terminate child PID={child.pid}: {e}")

    if edge_off is not None:
        logger.info(f"[CLEANUP] EdgeOff thread check: {edge_off.name}")
        if edge_off.is_alive():
            logger.warning("[CLEANUP] EdgeOffloading thread is still alive. Attempting graceful shutdown...")
            try:
                edge_off.stop_event.set()
            except Exception as e:
                logger.warning(f"[CLEANUP] Failed to set stop_event: {e}")

            edge_off.join(timeout=5)
            if edge_off.is_alive():
                logger.error("[FORCE] EdgeOffloading thread is STILL hanging after join.")
            else:
                logger.info("[CLEANUP] EdgeOffloading thread joined successfully.")
        else:
            logger.info("[CLEANUP] EdgeOffloading already stopped.")
    else:
        logger.info("[CLEANUP] No edge_off instance provided (None)")

random.seed (42)
# public variables
reg_nodes = list ()
cached_trx = list ()
update_thread = False
running_processes = []
#req_q, rsp_q = Queue (), Queue ()
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
    MAIN_PID = os.getpid()
    atexit.register(cleanup_ganache_processes)
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)
    clean_ganache_temp([])
    init_sensitivity_csvs()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=["fresco_sweep", "ode_all", "ode"],
        help="Execution mode: 'fresco_sweep' for param grid, 'ode_all' for all engines, 'ode' for one specific engine"
    )
    parser.add_argument("--multi-chain", action="store_true")
    parser.add_argument("--profile", choices=["default", "ar"], default="default",
                        help="Workload profile to use: 'default' or 'ar'")
    parser.add_argument(
      '--app', type=str, default='random',
      choices=['random', 'mobiar', 'intrasafed', 'naviar'],
      help="App deployment mode: 'random' for LiveLab sampling or fixed: 'mobiar', 'intrasafed', 'naviar'"
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=5,
        help="Maximum number of simulation processes running in parallel",
    )
    parser.add_argument(
        "--ode",
        type=str,
        choices=["fresco", "sq", "smt", "mdp", "qrl"],
        help="Run only a specific offloading decision engine (mutually exclusive with fresco_sweep)",
    )
    parser.add_argument(
        '--all-apps', action='store_true',
        help='Run the chosen ODE for all applications in parallel'
    )
    args = parser.parse_args()

    if not args.multi_chain and (args.mode == "fresco_sweep" or args.ode in ("fresco", "sq")):
        ganache_proc = start_ganache_instance(8545)

        # Deploy contract if not already done
        deployer = ChainHandler(Testnets.GANACHE, account_index=0)
        contract_address = deployer.deploy_smart_contract()
        with open("contract_address.txt", "w") as f:
            f.write(contract_address)

    if args.mode == 'fresco_sweep':
        app = None if args.app.lower() == 'random' else args.app.upper()
        k = 5
        base_port = 8545
        suffix = 1
        max_parallel = args.max_parallel
        step = 0.2
        values = [round(x * step, 2) for x in range(int(1 / step) + 1)]
        gammas = [0.2, 0.4, 0.6]
        param_combinations = []

        for gamma in gammas:
            for alpha in values:
                for beta in values:
                    if round(alpha + beta + gamma, 2) == 1.0:
                        param_combinations.append((alpha, beta, gamma))

        # add myopic collapse parameter configs
        param_combinations.extend([
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        ])

        logger.info(f"[INFO] Launching {len(param_combinations)} FRESCO configs")
        logger.info(f"[INFO] Max parallel processes: {max_parallel}")
        used_ports = set()
        ganache_procs = [] 
        # Batch execution
        for i in range(0, len(param_combinations), max_parallel):
            batch = param_combinations[i:i + max_parallel]
            processes = []

            for alpha, beta, gamma in batch:
                if args.multi_chain:
                    port = find_available_port(base_port + suffix, used_ports)
                    suffix = port - base_port  # Bind suffix to port offset
                    os.environ["MULTICHAIN"] = "1"
                    ganache_proc = start_ganache_instance(port)
                    ganache_procs.append(ganache_proc)
                else:
                    port = 8545

                proc = Process(
                    target=run_fresco_sim,
                    args=(alpha, beta, gamma, k, app, suffix, args.profile),
                    kwargs={"port": port, "sweep": args.mode == "fresco_sweep"}
                )
                proc.start()
                processes.append(proc)
                running_processes.append(proc)
                logger.info(f"[SPAWN] α={alpha}, β={beta}, γ={gamma}, port={port}")

        # Wait for current batch to finish before starting next
            for proc in processes:
                proc.join()
            
            if args.multi_chain:
                cleanup_ganache_processes()  # ✅ Only clean up if using multichain

        if args.multi_chain:
            cleanup_ganache_processes()
        else:
            cleanup_ganache_processes(proc=ganache_proc)

    elif args.mode == "ode_all":
      # 1. Clean stale Ganache processes first (system-wide safety)
      cleanup_ganache_processes()

      app = None if args.app.lower() == "random" else args.app.upper()
      suffix = 1
      port_base = 8545
      used_ports = set()

      models = ["fresco", "sq", "smt", "mdp", "qrl"]
      processes = []
      ganache_procs = []

      try:
        for model in models:
            suffix += 1

            if model in ("fresco", "sq"):
                port = find_available_port(port_base + suffix, used_ports)
                os.environ["MULTICHAIN"] = "1"

                logger.info(f"[GANACHE] Launching Ganache for {model.upper()} on port {port}")
                ganache_proc = start_ganache_instance(port)
                ganache_procs.append(ganache_proc)

            if model == "fresco":
                proc = Process(
                    target=run_fresco_sim,
                    args=(Settings.W_RT, Settings.W_EC, Settings.W_PR, Settings.K, app, suffix, args.profile),
                    kwargs={"port": port, "sweep": args.mode == "fresco_sweep"}
                )
            else:
                proc = Process(
                    target=run_simulation,
                    args=(model, app, suffix, args.profile, port)
                )

            proc.start()
            processes.append(proc)
            running_processes.append(proc)
            logger.info(f"[SPAWN] {model.upper()} launched with suffix={suffix}, port={port}")

        for proc in processes:
            proc.join()
        
        logger.warning("[CLEANUP] Cleaning everything...")
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
        cleanup_ganache_processes()
         # ✅ NEW: Poll for completion with timeout

      finally:
        logger.warning("[CLEANUP] Cleaning everything...")
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
        cleanup_ganache_processes()

    elif args.mode == "ode":
        if not args.ode:
            raise ValueError("ODE engine must be specified with --ode when using mode 'ode'")
      
        if args.all_apps:
            apps = ["mobiar", "naviar", "intrasafed", "random"]
            processes = []
            ganache_procs = []
            used_ports = set()
            suffix = 0

            for app_name in apps:
                suffix += 1
                port = 8545
                ganache_proc = None
                
                if args.multi_chain and args.ode in ("fresco", "sq"):
                    port = find_available_port(8545 + suffix, used_ports)
                    os.environ["MULTICHAIN"] = "1"
                    ganache_proc = start_ganache_instance(port)
                    ganache_procs.append(ganache_proc)

                if args.ode == "fresco":
                    proc = Process(
                        target=run_fresco_sim,
                        args=(Settings.W_RT, Settings.W_EC, Settings.W_PR, Settings.K,
                              None if app_name == "random" else app_name.upper(),
                              suffix, args.profile),
                        kwargs={"port": port}
                    )
                else:
                    proc = Process(
                        target=run_simulation,
                        args=(args.ode,
                              None if app_name == "random" else app_name.upper(),
                              suffix, args.profile, port)
                    )

                proc.start()
                processes.append(proc)
                running_processes.append(proc)

            for proc in processes:
                proc.join()

            if args.multi_chain:
                cleanup_ganache_processes()
        else:
            app = None if args.app.lower() == "random" else args.app.upper()
            suffix = 1
            port = 8545
            used_ports = set()
            ganache_proc = None

            if args.multi_chain and args.ode in ("fresco", "sq"):
                suffix = 1
                port = find_available_port(8545 + suffix, used_ports)
                os.environ["MULTICHAIN"] = "1"
                ganache_proc = start_ganache_instance(port)
            else:
                suffix = 0  # ✅ Important: matches account_index used during contract deployment
                port = 8545

            if args.ode == "fresco":
                proc = Process(
                    target=run_fresco_sim,
                    args=(Settings.W_RT, Settings.W_EC, Settings.W_PR, Settings.K, app, suffix, args.profile),
                    kwargs={"port": port}
                )
            else:
                proc = Process(
                    target=run_simulation,
                    args=(args.ode, app, suffix, args.profile, port)
                )

            proc.start()
            running_processes.append(proc)
            proc.join()

            if args.multi_chain:
                cleanup_ganache_processes(proc=ganache_proc)
