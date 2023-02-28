import re
import matplotlib.pyplot as plt
import numpy as np

from util import MobApps


def overhead_plot ():

	scale_nodes = [4, 20, 40, 60, 120, 200, 320, 400]
	smt_overhead = list ()

	for scala in [1, 5, 10, 15, 30, 50, 80, 100]:
		
		overhead_file = open ("logs/backup_logs/overhead/scala_" + str (scala) + ".txt", "r")
		smt_ovr_samples = list ()

		for line in overhead_file.readlines ():

			matched = re.search("Time elapsed for SMT computing is (\d+\.\d+) s", line)
			
			if matched:

				smt_ovr_samples.append (float (matched.group (1)))

		# print ('Average SMT overhead (' + str(scala * 4 + 1) + ' nodes) is ' + \
		# 	str (round (sum (smt_overhead) / len (smt_overhead), 4)) + ' s')
		smt_overhead.append (round (sum (smt_ovr_samples) / len (smt_ovr_samples), 4))

	plt.rcParams.update({'font.size': 16})
	# plotting the points 
	plt.plot(scale_nodes, smt_overhead)
	  
	# naming the x axis
	plt.xlabel('Number of nodes')
	# naming the y axis
	plt.ylabel('Time (s)')
	  	  
	# function to show the plot
	plt.show()


def plot_objective (regex_exp, y_axis_title, show):

	app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
	x = np.arange(len(app_names))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = list ()
		for app_n in app_names:

			f = open("logs/backup_logs/1_mal_node/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search(regex_exp, line)
				if matched:
					
					result[ode_n].append (float (matched.group (1)))

	plt.rcParams.update({'font.size': 16})
	ax = plt.subplot(111)
	ax.bar(x - 0.2, result['Rep-SMT'], width = 0.1, color = 'red', \
		align = 'center', label = 'Rep-SMT')
	ax.bar(x - 0.1, result['SMT'], width = 0.1, color = 'green', \
		align = 'center', label = 'SMT')
	ax.bar(x + 0, result['SQ'], width = 0.1, color = 'yellow', \
		align = 'center', label = 'SQ')
	ax.bar(x + 0.1, result['MDP'], width = 0.1, color = 'purple', \
		align = 'center', label = 'MDP')

	plt.xlabel('Mobile applications')
	plt.ylabel(y_axis_title)
	#plt.title('Average response time')
	plt.xticks(x, app_names, fontsize = 16)
	
	if show:
		plt.legend()
	
	plt.show()


def print_distribution ():

	NAVIAR_TASKS = 100 * 8
	app_n = MobApps.NAVIAR
	mal_scenarios = ["MAL1/5", "MAL2/5a", "MAL2/5b", "MAL2/5c"]
	x = np.arange(len(mal_scenarios))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = { 'ED1': [], 'EC1': [], 'ER1': [], 'CD1': [], 'MD1': []}
		for mal in mal_scenarios:

			if mal == "MAL1/5":
				
				f = open("logs/backup_logs/1_mal_node/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5a":

				f = open("logs/backup_logs/2_mal_nodes/EC_ER/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5b":

				f = open("logs/backup_logs/2_mal_nodes/EC_ED/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5c":

				f = open("logs/backup_logs/2_mal_nodes/ER_ED/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search("Offloading distribution \(percentage\): {'ED1': (\d+\.\d+), 'EC1': (\d+\.\d+), " + 
					"'ER1': (\d+\.\d+), 'CD1': (\d+\.\d+), 'MD1': (\d+\.\d+)}", line)
				if matched:
					
					result[ode_n]['ED1'].append (float (matched.group (1)))
					result[ode_n]['EC1'].append (float (matched.group (2)))
					result[ode_n]['ER1'].append (float (matched.group (3)))
					result[ode_n]['CD1'].append (float (matched.group (4)))
					result[ode_n]['MD1'].append (float (matched.group (5)))

	print ('Offloading distribution: ' + str (result))


def plot_dropping_rates ():

	NAVIAR_TASKS = 100 * 8
	app_n = MobApps.NAVIAR
	mal_scenarios = ["MAL1/5", "MAL2/5a", "MAL2/5b", "MAL2/5c"]
	x = np.arange(len(mal_scenarios))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = list ()
		for mal in mal_scenarios:

			if mal == "MAL1/5":
				
				f = open("logs/backup_logs/1_mal_node/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5a":

				f = open("logs/backup_logs/2_mal_nodes/EC_ER/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5b":

				f = open("logs/backup_logs/2_mal_nodes/EC_ED/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5c":

				f = open("logs/backup_logs/2_mal_nodes/ER_ED/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search("After 100 samples, average is (\d+\.\d+) QoS violations", line)
				if matched:
					
					result[ode_n].append (round ((float (matched.group (1)) / NAVIAR_TASKS) * 100, 3))

	plt.rcParams.update({'font.size': 16})
	ax = plt.subplot(111)
	ax.bar(x - 0.2, result['Rep-SMT'], width = 0.1, color = 'red', \
		align = 'center', label = 'Rep-SMT')
	ax.bar(x - 0.1, result['SMT'], width = 0.1, color = 'green', \
		align = 'center', label = 'SMT')
	ax.bar(x + 0, result['SQ'], width = 0.1, color = 'yellow', \
		align = 'center', label = 'SQ')
	ax.bar(x + 0.1, result['MDP'], width = 0.1, color = 'purple', \
		align = 'center', label = 'MDP')

	plt.ylabel('Offloading dropping rate (%)')
	plt.xlabel("Malicious scenarios")
	#plt.title('Average response time')
	plt.xticks(x, mal_scenarios, fontsize = 16)
	plt.legend()
	plt.show()


def plot_objective_with_mal (regex_exp, y_axis_title, show):

	app_n = MobApps.NAVIAR
	mal_scenarios = ["MAL1/5", "MAL2/5a", "MAL2/5b", "MAL2/5c"]
	x = np.arange(len(mal_scenarios))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = list ()
		for mal in mal_scenarios:

			if mal == "MAL1/5":
				
				f = open("logs/backup_logs/1_mal_node/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5a":

				f = open("logs/backup_logs/2_mal_nodes/EC_ER/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5b":

				f = open("logs/backup_logs/2_mal_nodes/EC_ED/sim_traces_" + ode_n + "_" + app_n + '.txt')

			elif mal == "MAL2/5c":

				f = open("logs/backup_logs/2_mal_nodes/ER_ED/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search(regex_exp, line)
				if matched:
					
					result[ode_n].append (float (matched.group (1)))

	plt.rcParams.update({'font.size': 16})
	ax = plt.subplot(111)
	ax.bar(x - 0.2, result['Rep-SMT'], width = 0.1, color = 'red', \
		align = 'center', label = 'Rep-SMT')
	ax.bar(x - 0.1, result['SMT'], width = 0.1, color = 'green', \
		align = 'center', label = 'SMT')
	ax.bar(x, result['SQ'], width = 0.1, color = 'yellow', \
		align = 'center', label = 'SQ')
	ax.bar(x + 0.1, result['MDP'], width = 0.1, color = 'purple', \
		align = 'center', label = 'MDP')

	plt.ylabel(y_axis_title)
	plt.xlabel("Malicious scenarios")
	#plt.title('Average response time')
	plt.xticks(x, mal_scenarios, fontsize = 16)
	
	if show:
		plt.legend()
	
	plt.show()

overhead_plot ()
# plot_objective ("After 100 samples, average is (\d+\.\d+) s", 'Response time (seconds)', True)
# plot_objective ("After 100 samples, average is (\d+\.\d+) % of energy remains", "Battery lifetime (%)", False)
# plot_objective ("After 100 samples, average is (\d+\.\d+) monetary units", "Monetary units", False)
# print_distribution ()
# plot_dropping_rates ()
# plot_objective_with_mal ("After 100 samples, average is (\d+\.\d+) s", 'Response time (seconds)', True)
# plot_objective_with_mal ("After 100 samples, average is (\d+\.\d+) % of energy remains", "Battery lifetime (%)", False)
# plot_objective_with_mal ("After 100 samples, average is (\d+\.\d+) monetary units", "Monetary units", False)