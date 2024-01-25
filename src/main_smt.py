import random
import datetime
from threading import Thread

from smt_ode import SmtOde
from sq_ode import SqOde
from mdp_ode import MdpOde
from mob_app_profiler import MobileAppProfiler
from res_mon import ResourceMonitor
from util import Settings


class EdgeOffloading (Thread):

	def __init__ (self, req_q, rsp_q, exe, samp, app_name, con_delay, scala, locs):

		Thread.__init__ (self)

		self._r_mon = ResourceMonitor (scala)
		self._m_app_prof = MobileAppProfiler ()
		self._s_ode = None
		self._req_q = req_q
		self._rsp_q = rsp_q
		self._exe = exe
		self._samp = samp
		self._app_name = app_name
		self._con_delay = con_delay
		self._scala = scala
		self._log = None
		
		# user moves to another cell location after certain number of applications excutions
		self._user_move = self._exe / locs
		# print ("User move: " + str (self._user_move))


	def deploy_rep_smt_ode (cls):

		cls._s_ode = SmtOde ('Rep-SMT', cls._r_mon.get_md (), cls._r_mon.get_md (), \
			cls._app_name, True, cls._con_delay, cls._scala)


	def deploy_smt_ode (cls):

		cls._s_ode = SmtOde ('SMT', cls._r_mon.get_md (), cls._r_mon.get_md (), \
			cls._app_name, False, cls._con_delay, cls._scala)


	def deploy_sq_ode (cls):

		cls._s_ode = SqOde ('SQ', cls._r_mon.get_md (), cls._r_mon.get_md (), cls._app_name, \
			cls._con_delay, cls._scala)


	def deploy_mdp_ode (cls):

		cls._s_ode = MdpOde ('MDP', cls._r_mon.get_md (), cls._r_mon.get_md (), \
			cls._app_name, cls._con_delay, cls._r_mon.get_off_sites (), cls._scala)


	def run (cls):

		cls._log = cls._s_ode.get_logger ()
		off_sites = cls._r_mon.get_off_sites ()
		topology = cls._r_mon.get_topology ()
		app = cls._m_app_prof.dep_app (cls._app_name)
		app.run ()

		# cls.__print_setup (off_sites, topology, app)
		off_sites = cls.__register_nodes (off_sites)

		# setting cell statistics (this is updated after each loading dataset nodes into off sites)
		cls._s_ode.set_cell_stats (cls._r_mon.get_cell_name ())

		epoch_cnt = 0 # counts task offloadings
		exe_cnt = 0   # counts application executions
		samp_cnt = 0  # counts samples
		period_cnt = 0 # counts number of task offloadings within single time period in cell location
		time_period = cls.__compute_time_period (app.get_num_of_tasks ())
		timestamp = 0.0
		prev_progress = 0
		curr_progress = 0
		con_delay = 0 # consensus delay constraint
		task_n_delay = "" # delay counter (counting epochs)
		off_transactions = list ()

		# cls._log.w ("APP EXECUTION No." + str (exe_cnt + 1))
		# cls._log.w ("SAMPLE No." + str (samp_cnt + 1))

		print ("**************** PROGRESS " + cls._s_ode.get_name() + "****************")
		print (str(prev_progress) + "% - " + str(datetime.datetime.utcnow()))

		while True:

			(curr_progress, prev_progress) = cls.__print_progress (exe_cnt, samp_cnt, \
				curr_progress, prev_progress)
						
			tasks = app.get_ready_tasks ()
			timestamp = round (time_period * period_cnt, 3)

			# when all application tasks are completed
			if len (tasks) == 0:
				
				app = cls._m_app_prof.dep_app (cls._app_name)
				app.run ()
				exe_cnt = exe_cnt + 1
				cls._s_ode.app_exc_done (app.get_qos ())

				# update reputation after each application execution and reset transaction list
				cls._req_q.put (('update', off_transactions))
				off_transactions = list ()
				# print ("Execution:" + str (exe_cnt))

				# when certain number of application executions are completed 
				# then mobile device moves to another cell location and 
				# new availability datasets are loaded per offloading site
				if exe_cnt % cls._user_move == 0:

					# print ("Cell move")
					period_cnt = 0

					# summarize cell statistics
					cls._s_ode.summarize_cell_stats (cls._r_mon.get_cell_name ())
					
					# load dataset by number of changed cell locations
					off_sites = cls._r_mon.load_datasets (int (exe_cnt / cls._user_move))

					# reset reputation when moved to a new cell location
					off_sites = cls.__reset_reputation (off_sites)

					# when new datasets are loaded then cell location is changed for statistics
					cls._s_ode.set_cell_stats (cls._r_mon.get_cell_name ())

				# cls._log.w ("APP EXECUTION No." + str (exe_cnt + 1))
				continue
			
			# consensus delay
			if tasks[0].get_name == task_n_delay:

				con_delay = con_delay + 1

			# incrementing epoch (i.e. task offloading) and period counter (i.e. epochs within same time period)
			epoch_cnt = epoch_cnt + 1
			period_cnt = period_cnt + 1
			# cls._log.w ('Time epoch ' + str (epoch_cnt) + '.')

			# all executions are completed
			if exe_cnt >= cls._exe:

				# summarize offloading results
				cls._s_ode.summarize ()

				# count new sample
				samp_cnt = samp_cnt + 1

				# reset execution counter
				exe_cnt = 0
				
				# if all samples are completed, end the experiment via message queue close
				if samp_cnt == cls._samp: 
						
					cls._s_ode.log_stats ()
					# cls.__reset_reputation (off_sites)
					cls._req_q.put (('close', [site.get_sc_id () for site in off_sites]))
					
					if cls._rsp_q.get () == 'confirm':
						# break from the run loop
						break
				
				# cls._log.w ("SAMPLE No." + str (samp_cnt + 1))
				app = cls._m_app_prof.dep_app (cls._app_name)
				app.run ()
				# off_sites = cls.__reset_reputation (off_sites)
				continue

			if con_delay == cls._con_delay:

				off_sites = cls.__get_reputation (off_sites)
				con_delay = 0
				task_n_delay = tasks[0].get_name ()
			
			# off_sites = cls.__update_behav (off_sites, exe_cnt)
			trxs = cls._s_ode.offload (tasks, off_sites, topology, timestamp, \
				app.get_name (), app.get_qos ())

			off_transactions += trxs

			if not off_transactions:

				exe_cnt = cls._exe
				continue


	def __compute_time_period (cls, num_of_tasks):

		return round (1 / (num_of_tasks * (cls._user_move)), 3)


	def __print_progress (cls, exe_cnt, samp_cnt, curr_progress, prev_progress):

		prev_progress = curr_progress
		curr_progress = round((exe_cnt + (samp_cnt * cls._exe)) / \
			(cls._samp * cls._exe) * 100)

		if curr_progress != prev_progress and (curr_progress % \
			Settings.PROGRESS_REPORT_INTERVAL == 0):
				
			print(str(curr_progress) + "% - " + str(datetime.datetime.utcnow()))

		return (curr_progress, prev_progress)


	def __register_nodes (cls, off_sites):

		names = [site.get_n_id () for site in off_sites]
		cls._req_q.put (('reg', names))
		reg_nodes = cls._rsp_q.get ()

		if reg_nodes[0] == 'reg_rsp':

			for ele in reg_nodes[1]:

				for site in off_sites:

					if ele['name'] == site.get_n_id ():

						site.set_sc_id (ele['id'])
						break

		return off_sites


	def __get_reputation (cls, off_sites):

		sc_ids = [site.get_sc_id () for site in off_sites]
		cls._req_q.put (('get', sc_ids))
		get_msg = cls._rsp_q.get ()

		if get_msg[0] == 'get_rsp':

			for site_rep in get_msg[1]:

				for site in off_sites:

					if site_rep[0] == site.get_sc_id ():

				 		site.set_reputation (site_rep[1])
				 		# cls._log.w (site.get_n_id () + " reputation is " + str (site.get_reputation ()))

		return off_sites


	def __print_setup (cls, off_sites, topology, app):

		print (topology)
		app.print_entire_config ()
	
		for off_site in off_sites:
	
			off_site.print_system_config ()


	def __reset_reputation (cls, off_sites):

		sc_ids = [site.get_sc_id () for site in off_sites]
		cls._req_q.put (('reset', sc_ids))
		reset_msg = cls._rsp_q.get ()

		if reset_msg[0] == 'reset_rsp':

			for site_rep in reset_msg[1]:

				for site in off_sites:

				 	if site_rep['id'] == site.get_sc_id ():

				 		site.set_reputation (site_rep['score'])
				 		# print (site.get_n_id () + " reputation reseted on " + str (site.get_reputation ()))
				 		# cls._log.w (site.get_n_id () + " reputation reseted on " + str (site.get_reputation ()))

		return off_sites
