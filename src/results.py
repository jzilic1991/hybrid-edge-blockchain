import re
import matplotlib.pyplot as plt
import numpy as np

from util import MobApps


def overhead_print ():

	overhead_file = open ("logs/backup_logs/overhead/SMT_overhead.txt", "r")
	smt_overhead = list ()

	for line in overhead_file.readlines ():

		matched = re.search("Time elapsed for SMT computing is (\d+\.\d+) s", line)
		if matched:

			smt_overhead.append (float (matched.group (1)))

	print ('Average SMT overhead is ' + str (round (sum (smt_overhead) / len (smt_overhead), 4)) + ' s')


def plot_objective (regex_exp, y_axis_title, show):

	app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
	x = np.arange(len(app_names))
	ode_names = ["Rep-SMT", "SMT", "SQ"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = list ()
		for app_n in app_names:

			f = open("logs/backup_logs/1_mal_node/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search(regex_exp, line)
				if matched:
					
					result[ode_n].append (float (matched.group (1)))

	plt.rcParams.update({'font.size': 14})
	ax = plt.subplot(111)
	ax.bar(x - 0.2, result['Rep-SMT'], width = 0.2, color = 'b', \
		align = 'center', label = 'Rep-SMT')
	ax.bar(x, result['SMT'], width = 0.2, color = 'pink', \
		align = 'center', label = 'SMT')
	ax.bar(x + 0.2, result['SQ'], width = 0.2, color = 'black', \
		align = 'center', label = 'SQ')

	plt.xlabel('Mobile applications')
	plt.ylabel(y_axis_title)
	#plt.title('Average response time')
	plt.xticks(x, app_names, fontsize = 14)
	
	if show:
		plt.legend()
	
	plt.show()


def print_distribution ():

	app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
	x = np.arange(len(app_names))
	ode_names = ["Rep-SMT", "SMT", "SQ"]
	result = { 'ED1': [], 'EC1': [], 'ER1': [], 'CD1': [], 'MD1': []}

	for ode_n in ode_names:
		
		for app_n in app_names:

			f = open("logs/backup_logs/1_mal_node/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search("Offloading distribution \(percentage\): {'ED1': (\d+\.\d+), 'EC1': (\d+\.\d+), 'ER1': (\d+\.\d+), 'CD1': (\d+\.\d+), 'MD1': (\d+\.\d+)}", line)
				
				if matched:
					
					result['ED1'].append (float (matched.group (1)))
					result['EC1'].append (float (matched.group (2)))
					result['ER1'].append (float (matched.group (3)))
					result['CD1'].append (float (matched.group (4)))
					result['MD1'].append (float (matched.group (5)))

	print ('Offloading distribution: ' + str (result))


# overhead_print ()
plot_objective ("After 100 samples, average is (\d+\.\d+) s", 'Response time (seconds)', True)
plot_objective ("After 100 samples, average is (\d+\.\d+) % of energy remains", "Battery lifetime (%)", False)
plot_objective ("After 100 samples, average is (\d+\.\d+) monetary units", "Monetary units", False)
# print_distribution ()