from smt_ode import SmtOde
from mob_app_profiler import MobileAppProfiler
from res_mon import ResourceMonitor
from models import Model


def print_setup (off_sites, topology, app):
	
	for off_site in off_sites:
	
		off_site.print_system_config ()
		print (topology)
		app.print_entire_config ()


# class instances
r_mon = ResourceMonitor ()
m_app_prof = MobileAppProfiler ()
s_ode = SmtOde ('SMT_ODE', r_mon.get_md (), r_mon.get_md ())

# infrastructure and application resource information
off_sites = r_mon.get_off_sites ()
topology = r_mon.get_topology ()
app = m_app_prof.dep_rand_mob_app ()
app.run ()

print_setup (off_sites, topology, app)

i = 0

# start offloading
while True:

	tasks = app.get_ready_tasks ()

	if len(tasks) == 0:
		break
		
	i = i + 1
	print ('Time epoch ' + str(i) + '.')
	(max_rt, acc_ec, acc_pr) = s_ode.offload (tasks, off_sites, topology)
	print ("Max RT: " + str (max_rt) + ", Acc EC: " + str (acc_ec) + \
		", Acc PR: " + str (acc_pr))
	print ()