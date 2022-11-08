from smt_ode import SmtOde
from mob_app_profiler import MobileAppProfiler
from res_mon import ResourceMonitor
from models import Model


r_mon = ResourceMonitor ()
m_app_prof = MobileAppProfiler ()
s_ode = SmtOde ('SMT_ODE', r_mon.get_md ())

off_sites = r_mon.get_off_sites ()
topology = r_mon.get_topology ()
app = m_app_prof.dep_rand_mob_app ()
app.run ()

for off_site in off_sites:
	
	off_site.print_system_config ()

print (topology)
app.print_entire_config ()
i = 0

while True:

	tasks = app.get_ready_tasks ()

	if len(tasks):
		
		i = i + 1
		print ('Time epoch ' + str(i) + '.')
		print (s_ode.offload (tasks, off_sites, topology))
		print ()

	else:

		break