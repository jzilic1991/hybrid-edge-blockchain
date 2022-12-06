from res_mon import ResourceMonitor
from mdp_ode import MdpOde
from util import MobApps

r_mon = ResourceMonitor ()
ode = MdpOde ('MDP', r_mon.get_md (), r_mon.get_md (), MobApps.NAVIAR, 2, r_mon.get_off_sites ())