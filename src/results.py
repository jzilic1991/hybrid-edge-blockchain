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
	# app_names = [MobApps.NAVIAR]
	x = np.arange(len(app_names))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = list ()
		
		for app_n in app_names:

			f = open("results/sim_traces_" + ode_n + "_" + app_n + '.txt')

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
	
	# showing legend on the figure or not
	if show:
		plt.legend()
	
	plt.show()


def stacked_bar(data, series_labels, color_labels, category_labels = None, 
                show_values = False, value_format = "{}", y_label = None, 
                grid = False, reverse = False):
    """Plots a stacked bar chart with the data and labels provided.

    Keyword arguments:
    data            -- 2-dimensional numpy array or nested list
                       containing data for each series in rows
    series_labels   -- list of series labels (these appear in
                       the legend)
    category_labels -- list of category labels (these appear
                       on the x-axis)
    show_values     -- If True then numeric value labels will 
                       be shown on each bar
    value_format    -- Format string for numeric value labels
                       (default is "{}")
    y_label         -- Label for y-axis (str)
    grid            -- If True display grid
    reverse         -- If True reverse the order that the
                       series are displayed (left-to-right
                       or right-to-left)
    """

    ny = len(data[0])
    ind = list(range(ny))

    axes = []
    cum_size = np.zeros(ny)

    data = np.array(data)

    if reverse:
        data = np.flip(data, axis = 1)
        category_labels = reversed(category_labels)

    for i, row_data in enumerate(data):
        axes.append(plt.bar(ind, row_data, bottom = cum_size, color = color_labels[i],
                            label = series_labels[i]))
        cum_size += row_data

    if category_labels:
        plt.xticks(ind, category_labels)

    if y_label:
        plt.ylabel(y_label)

    plt.legend(bbox_to_anchor = (1.04,1), loc = "upper left", prop = {'size': 14}, framealpha = 1, frameon = True)

    if grid:
        plt.grid()

    if show_values:
        for axis in axes:
            for bar in axis:
                w, h = bar.get_width(), bar.get_height()
                if h != 0.0:
                    plt.text(bar.get_x() + w/2, bar.get_y() + h/2, 
                             value_format.format(h), ha = "center", 
                             va = "center")


def plot_offloading_distribution():
    plt.rcParams.update({'font.size': 16})
    # key: ODE, value: {key: app, value: {key: site, value: distribution percentage}}}
    offload_dist_dict = dict ()
	app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
	x = np.arange(len(app_names))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()
	regex_ex = "Offloading distribution (percentage): {'(ED.+)': (\d+\.\d+)," + \
	"'(EC.+)': (\d+\.\d+)', '(ER.+)': (\d+\.\d+)'," + \
	"'(CD.+)': (\d+\.\d+), '(MD.+)': (\d+\.\d+)}"

	for ode_n in ode_names:
		
		result [ode_n] = list ()
		
		for app_n in app_names:

			f = open("results/sim_traces_" + ode_n + "_" + app_n + '.txt')

			for line in f.readlines ():

				matched = re.search(regex_exp, line)
				if matched:
					
					result[ode_n].append (float (matched.group (1)))

    series_labels = ['MD', 'ER', 'ED', 'Cloud', 'EC']
    color_labels = ['y', 'mediumslateblue', 'pink',  'lightyellow', 'slateblue']

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])

    stacked_bar(data,
               series_labels,
               color_labels,
               category_labels = category_labels, 
               show_values = True, 
               value_format = "{:.2f}",
               y_label = "Quantity (units)") 

    ax.set_xlabel('Offloading decision engines', fontsize = 16)
    ax.set_ylabel('Distribution (%)', fontsize = 16)
    ax.set_ylim(0, 102)
        plt.show()


def print_distribution ():

	# NAVIAR_TASKS = 100 * 8
	app_n = MobApps.NAVIAR
	# mal_scenarios = ["MAL1/5", "MAL2/5a", "MAL2/5b", "MAL2/5c"]
	# x = np.arange(len(mal_scenarios))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()

	for ode_n in ode_names:
		
		result [ode_n] = { 'ED1': [], 'EC1': [], 'ER1': [], 'CD1': [], 'MD1': []}
		for mal in mal_scenarios:

			f = open("results/sim_traces_" + ode_n + "_" + app_n + '.txt')

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

	# NAVIAR_TASKS = 100 * 8
	app_n = [MobApps.NAVIAR, MobApps.MOBIAR, MobApps.INTRASAFED]
	# mal_scenarios = ["MAL1/5", "MAL2/5a", "MAL2/5b", "MAL2/5c"]
	x = np.arange(len(app_n))
	ode_names = ["Rep-SMT", "SMT", "SQ", "MDP"]
	result = dict ()
	# flag to detect when final part of result log will be parsed 
	# for summarizing overall task failure rate
	summary_flag = False

	for ode_n in ode_names:
		
		result [ode_n] = list ()

		for app in app_n:

			f = open("results/sim_traces_" + ode_n + "_" + app + '.txt')
			
			# reset the flag when reading a next file
			summary_flag = False

			for line in f.readlines ():

				if not summary_flag:

					matched = re.search("After 100 samples, average is (\d+\.\d+) QoS violations", line)

					if matched:
						
						summary_flag = True

				else:

					matched = re.search("Average task failure rate \(percentage\) is (\d+\.\d+)", line)
					
					if matched:
						
						# casting parsed string into float
						result[ode_n] = float (matched.group (1))


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

	plt.ylabel('Task failure rate (%)')
	plt.xlabel("Offloading decision engine")
	plt.xticks(x, app_n, fontsize = 16)
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

# overhead_plot ()
plot_objective ("After 100 samples, average is (\d+\.\d+) s", 'Response time (seconds)', True)
plot_objective ("After 100 samples, average is (\d+\.\d+) % of energy remains", "Battery lifetime (%)", True)
plot_objective ("After 100 samples, average is (\d+\.\d+) monetary units", "Monetary units", True)
# print_distribution ()
plot_offloading_distribution ()
plot_dropping_rates ()
# plot_objective_with_mal ("After 100 samples, average is (\d+\.\d+) s", 'Response time (seconds)', True)
# plot_objective_with_mal ("After 100 samples, average is (\d+\.\d+) % of energy remains", "Battery lifetime (%)", False)
# plot_objective_with_mal ("After 100 samples, average is (\d+\.\d+) monetary units", "Monetary units", False)