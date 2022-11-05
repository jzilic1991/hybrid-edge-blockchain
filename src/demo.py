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
s_ode.offload (app.get_ready_tasks (), off_sites, topology)