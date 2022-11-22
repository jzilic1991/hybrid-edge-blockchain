import random
import datetime
from threading import Thread

from smt_ode import SmtOde
from sq_ode import SqOde
from mob_app_profiler import MobileAppProfiler
from res_mon import ResourceMonitor
from util import Settings


class EdgeOffloading (Thread):

	def __init__ (self, req_q, rsp_q, exe, samp):

		Thread.__init__ (self)
		self._r_mon = ResourceMonitor ()
		self._m_app_prof = MobileAppProfiler ()
		self._s_ode = None
		self._req_q = req_q
		self._rsp_q = rsp_q
		self._exe = exe
		self._samp = samp
		self._log = None


	def deploy_smt_ode (cls):

		cls._s_ode = SmtOde ('SMT_ODE', cls._r_mon.get_md (), cls._r_mon.get_md ())


	def deploy_sq_ode (cls):

		cls._s_ode = SqOde ('SQ_ODE', cls._r_mon.get_md (), cls._r_mon.get_md ())


	def run (cls):

		cls._log = cls._s_ode.get_logger ()
		off_sites = cls._r_mon.get_off_sites ()
		topology = cls._r_mon.get_topology ()
		app = cls._m_app_prof.dep_rand_mob_app ()
		app.run ()

		# cls.__print_setup (off_sites, topology, app)
		off_sites = cls.__register_nodes (off_sites)

		epoch_cnt = 0 # counts task offloadings
		exe_cnt = 0   # counts application executions
		samp_cnt = 0  # counts samples
		prev_progress = 0
		curr_progress = 0

		cls._log.w ("APP EXECUTION No." + str (exe_cnt + 1))
		cls._log.w ("SAMPLE No." + str (samp_cnt + 1))

		print ("**************** PROGRESS " + cls._s_ode.get_name() + "****************")
		print (str(prev_progress) + "% - " + str(datetime.datetime.utcnow()))

		while True:

			(curr_progress, prev_progress) = cls.__print_progress (exe_cnt, samp_cnt, \
				curr_progress, prev_progress)
						
			tasks = app.get_ready_tasks ()

			if len(tasks) == 0:
				
				app = cls._m_app_prof.dep_rand_mob_app ()
				app.run ()
				exe_cnt = exe_cnt + 1
				cls._log.w ("APP EXECUTION No." + str (exe_cnt + 1))
				continue
				
			epoch_cnt = epoch_cnt + 1
			cls._log.w ('Time epoch ' + str (epoch_cnt) + '.')

			if exe_cnt == cls._exe:

				cls._s_ode.summarize ()
				samp_cnt = samp_cnt + 1
				exe_cnt = 0
									
				if samp_cnt == cls._samp: 
						
					cls._s_ode.log_stats ()
					# cls.__reset_reputation (off_sites)
					cls._req_q.put (('close', [site.get_sc_id () for site in off_sites]))
					if cls._rsp_q.get () == 'confirm': 

						break

				cls._log.w ("SAMPLE No." + str (samp_cnt + 1))
				app = cls._m_app_prof.dep_rand_mob_app ()
				app.run ()
				off_sites = cls.__reset_reputation (off_sites)
				continue

			off_sites = cls.__get_reputation (off_sites)
			off_sites = cls.__update_behav (off_sites)
			off_transactions = cls._s_ode.offload (tasks, off_sites, topology)
			cls._req_q.put (('update', off_transactions))


	def __print_progress (cls, exe_cnt, samp_cnt, curr_progress, prev_progress):

		prev_progress = curr_progress
		curr_progress = round((exe_cnt + (samp_cnt * cls._exe)) / (cls._samp * cls._exe) * 100)

		if curr_progress != prev_progress and (curr_progress % Settings.PROGRESS_REPORT_INTERVAL == 0):
				
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
				 		cls._log.w (site.get_n_id () + " reputation is " + str (site.get_reputation ()))

		return off_sites


	def __print_setup (cls, off_sites, topology, app):

		print (topology)
		app.print_entire_config ()
	
		for off_site in off_sites:
	
			off_site.print_system_config ()


	def __update_behav (cls, off_sites):

		for site in off_sites:

			if site.get_n_id () == "EC1":
				
				site.set_mal_behav (True)

			else:

				site.set_mal_behav (False)

		return off_sites


	def __reset_reputation (cls, off_sites):

		sc_ids = [site.get_sc_id () for site in off_sites]
		cls._req_q.put (('reset', sc_ids))
		reset_msg = cls._rsp_q.get ()

		if reset_msg[0] == 'reset_rsp':

			for site_rep in reset_msg[1]:

				for site in off_sites:

				 	if site_rep['id'] == site.get_sc_id ():

				 		site.set_reputation (site_rep['score'])
				 		cls._log.w (site.get_n_id () + " reputation reseted on " + str (site.get_reputation ()))

		return off_sites