import random
from threading import Thread

from smt_ode import SmtOde
from mob_app_profiler import MobileAppProfiler
from res_mon import ResourceMonitor


class EdgeOffloading (Thread):

	def __init__ (self, req_q, rsp_q):

		Thread.__init__ (self)
		self._r_mon = ResourceMonitor ()
		self._m_app_prof = MobileAppProfiler ()
		self._s_ode = SmtOde ('SMT_ODE', self._r_mon.get_md (), self._r_mon.get_md ())
		self._req_q = req_q
		self._rsp_q = rsp_q


	def run (cls):

		off_sites = cls._r_mon.get_off_sites ()
		topology = cls._r_mon.get_topology ()
		app = cls._m_app_prof.dep_rand_mob_app ()
		app.run ()

		# cls.__print_setup (off_sites, topology, app)
		off_sites = cls.__register_nodes (off_sites)

		epoch_cnt = 0
		while True:

			tasks = app.get_ready_tasks ()

			if len(tasks) == 0:
				
				app = cls._m_app_prof.dep_rand_mob_app ()
				app.run ()
				cls._s_ode.summarize ()
				continue
				
			epoch_cnt = epoch_cnt + 1
			print ('Time epoch ' + str (epoch_cnt) + '.')

			if epoch_cnt == 150:

				cls._req_q.put (('close'))
				if cls._rsp_q.get () == 'confirm': 

					cls._s_ode.summarize ()
					cls._s_ode.print_stats ()
					print ('CHILD THREAD is done.')
					break

			off_sites = cls.__get_reputation (off_sites)
			off_transactions = cls._s_ode.offload (tasks, off_sites, topology)
			cls._req_q.put (('update', off_transactions))
			# cls.__update_reputation (cls._s_ode.get_current_site ())
			# print ("Max RT: " + str (max_rt) + ", Acc EC: " + str (acc_ec) + \
			# 	", Acc PR: " + str (acc_pr))
			# print ()


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
				 		break

		return off_sites


	# def __update_reputation (cls, curr_n):

	# 	cls._req_q.put (('update', curr_n.get_sc_id (), int(round(random.uniform (0, 1), 3) * 1000)))


	def __print_setup (cls, off_sites, topology, app):

		print (topology)
		app.print_entire_config ()
	
		for off_site in off_sites:
	
			off_site.print_system_config ()


# # class instances
# r_mon = ResourceMonitor ()
# m_app_prof = MobileAppProfiler ()
# s_ode = SmtOde ('SMT_ODE', r_mon.get_md (), r_mon.get_md ())

# # infrastructure and application resource information
# off_sites = r_mon.get_off_sites ()
# topology = r_mon.get_topology ()
# app = m_app_prof.dep_rand_mob_app ()
# app.run ()

# print_setup (off_sites, topology, app)

# i = 0

# start offloading
# while True:

# 	tasks = app.get_ready_tasks ()

# 	if len(tasks) == 0:
# 		break
		
# 	i = i + 1
# 	print ('Time epoch ' + str(i) + '.')
# 	(max_rt, acc_ec, acc_pr) = s_ode.offload (tasks, off_sites, topology)
# 	print ("Max RT: " + str (max_rt) + ", Acc EC: " + str (acc_ec) + \
# 		", Acc PR: " + str (acc_pr))
# 	print ()