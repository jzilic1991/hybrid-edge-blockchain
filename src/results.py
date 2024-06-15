import sys
import re
import matplotlib.pyplot as plt
import numpy as np

from util import MobApps


def overhead_plot ():
  data = dict ()
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
  app_names = [MobApps.INTRASAFED]#, MobApps.MOBIAR, MobApps.NAVIAR]

  for ode in ode_names:
    data[ode] = list ([list (), list ()])
    tmp = list ()
    
    for app in app_names:
      overhead_file = open ("logs/sim_traces_" + str (ode) + "_" + str (app) + ".txt", "r")
      
      for line in overhead_file.readlines ():
        matched = re.search("Offloading decision time overhead: \((\d+) nodes, (\d+\.\d+) s\)", line)

        if matched:
          tmp.append ((int (matched.group (1)), float (matched.group (2)) * 1000))
          # data[ode][0].append (int (matched.group (1)))
          # data[ode][1].append (float (matched.group (2)) * 1000)

        matched = re.search("Offloading decision time overhead: \((\d+) nodes, (\d+(\.\d+)([eE]-\d+)) s\)", line)
        if matched:
          tmp.append ((int (matched.group (1)), float (matched.group (2)) * 1000))
          # data[ode][0].append (int (matched.group (1)))
          # data[ode][1].append (float (matched.group (2)) * 1000)

    tmp = sorted (tmp, key = lambda x: x[1])
    for ele in tmp:
      data[ode][0].append (ele[0])
      data[ode][1].append (ele[1])

  plt.rcParams.update({'font.size': 16})
  plt.scatter(data[ode_names[0]][0], np.log (data[ode_names[0]][1]), marker = 'o', color = 'red', label = ode_names[0])
  plt.scatter(data[ode_names[1]][0], np.log (data[ode_names[1]][1]), marker = 'x', color = 'blue', label = ode_names[1])
  plt.scatter(data[ode_names[2]][0], np.log (data[ode_names[2]][1]), marker = '.', color = 'green', label = ode_names[2])
  plt.scatter(data[ode_names[3]][0], np.log (data[ode_names[3]][1]), marker = '^', color = 'magenta', label = ode_names[3])
  plt.xlabel('Number of nodes')
  plt.ylabel('Time (ms)')
  plt.tight_layout ()
  plt.legend()
  plt.show()

  overhead_print (data)


def overhead_print (data):
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]

  print ("Average time overhead:")
  for i in range (len (ode_names)):
    print (ode_names[i] + ": " + str (np.mean (data[ode_names[i]][1])) + " ms (" + str (data[ode_names[i]][1]) + ")" + \
      ", std: " + str (np.std (data[ode_names[i]][1])))


def plot_objective (regex_exp, y_axis_title, show):
  app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
  x = np.arange(len (app_names))
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
  yerr_ode = {"FRESCO": 0.0, "SMT": 0.0, "SQ": 0.0, "MDP": 0.0}
  result = dict ()

  for ode_n in ode_names:
    result [ode_n] = list ()

    for app_n in app_names:
      f = open("logs/sim_traces_" + ode_n + "_" + app_n + '.txt')

      for line in f.readlines ():
        matched = re.search(regex_exp, line)

        if matched:
          result[ode_n].append (float (matched.group (1)))
          yerr_ode[ode_n] = float (matched.group (3))

  plt.rcParams.update({'font.size': 16})
  ax = plt.subplot(111)
  ax.bar(x - 0.2, result['FRESCO'], yerr = yerr_ode['FRESCO'], width = 0.1, color = 'red', \
    align = 'center', label = 'FRESCO', capsize=3)
  ax.bar(x - 0.1, result['SMT'], yerr = yerr_ode['SMT'], width = 0.1, color = 'green', \
    align = 'center', label = 'SMT', capsize=3)
  ax.bar(x + 0, result['SQ'], yerr = yerr_ode['SQ'], width = 0.1, color = 'yellow', \
    align = 'center', label = 'SQ', capsize=3)
  ax.bar(x + 0.1, result['MDP'], yerr = yerr_ode['MDP'], width = 0.1, color = 'purple', \
    align = 'center', label = 'MDP', capsize=3)

  plt.xlabel('Mobile applications')
  plt.ylabel(y_axis_title)
  #plt.title('Average response time')
  plt.xticks(x, app_names, fontsize = 16)

  if y_axis_title == "Battery lifetime (%)":
    ax.set_ylim (90, 100)

  # showing legend on the figure or not
  if show:
    plt.legend()

  plt.tight_layout ()
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

    plt.tight_layout ()
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


def plot_offloading_distributions (samples):
  plt.rcParams.update({'font.size': 16})
  # key: ODE, value: {key: app, value: {key: site, value: distribution percentage}}}
  offload_dist_dict = dict ()
  app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
  x = np.arange(len(app_names))
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
  result = dict ()
  regex_ex = "Offloading distribution \(percentage\): {'(ER[^']*'): (\d+\.\d+), '(ED[^']*'): (\d+\.\d+)," + \
    " '(EC[^']*'): (\d+\.\d+), '(CD[^']*'): (\d+\.\d+), '(MD[^']*'): (\d+\.\d+)}"

  for ode_n in ode_names:
    result [ode_n] = dict ()
    
    for app_n in app_names:
      result [ode_n][app_n] = {"CD": 0.0, "MD": 0.0, "ED": 0.0, "EC": 0.0, "ER": 0.0}
      f = open("logs/sim_traces_" + ode_n + "_" + app_n + '.txt')
      summary_flag = False

      for line in f.readlines ():
        if not summary_flag:
          matched = re.search("After (\d+) samples, average is (\d+\.\d+) % QoS violation rate(.*)", line)

          if matched:
            summary_flag = True
        
        else:
          matched = re.search(regex_ex, line)
          if matched:
            
            result[ode_n][app_n]["ED"] = float (matched.group (2))
            result[ode_n][app_n]["EC"] = float (matched.group (4))
            result[ode_n][app_n]["ER"] = float (matched.group (6))
            result[ode_n][app_n]["CD"] = float (matched.group (8))
            result[ode_n][app_n]["MD"] = float (matched.group (10))

  # print (result)
  # exit ()
  for app in app_names:

    data = list ()
    data.append ((result[ode_names[0]][app]["MD"], result[ode_names[1]][app]["MD"], \
      result[ode_names[2]][app]["MD"], result[ode_names[3]][app]["MD"]))
    data.append ((result[ode_names[0]][app]["ER"], result[ode_names[1]][app]["ER"], \
      result[ode_names[2]][app]["ER"], result[ode_names[3]][app]["ER"]))
    data.append ((result[ode_names[0]][app]["ED"], result[ode_names[1]][app]["ED"], \
      result[ode_names[2]][app]["ED"], result[ode_names[3]][app]["ED"]))
    data.append ((result[ode_names[0]][app]["CD"], result[ode_names[1]][app]["CD"], \
      result[ode_names[2]][app]["CD"], result[ode_names[3]][app]["CD"]))
    data.append ((result[ode_names[0]][app]["EC"], result[ode_names[1]][app]["EC"], \
      result[ode_names[2]][app]["EC"], result[ode_names[3]][app]["EC"]))

    series_labels = ['MD', 'ER', 'ED', 'CD', 'EC']
    color_labels = ['lightgreen', 'lightblue', 'lightpink', 'yellow', 'lavender']

    fig = plt.figure(figsize = (8, 6))
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])

    stacked_bar(data,
          series_labels,
          color_labels,
          category_labels = ode_names,
          show_values = True, 
          value_format = "{:.2f}",
          y_label = "Quantity (units)") 

    # ax.set_title (app + " application")
    ax.set_xlabel('Offloading decision engines', fontsize = 16)
    ax.set_ylabel('Distribution (%)', fontsize = 16)
    ax.set_ylim(0, 102)
    plt.tight_layout ()
    plt.show()


def print_constraint_violation_distribution (samples):
  plt.rcParams.update({'font.size': 16})
  # key: ODE, value: {key: app, value: {key: site, value: distribution percentage}}}
  offload_dist_dict = dict ()
  app_names = [MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR]
  x = np.arange(len(app_names))
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
  result = dict ()

  for ode_n in ode_names:
    result [ode_n] = dict ()
    
    for app_n in app_names:
      result [ode_n][app_n] = {"CD": 0.0, "MD": 0.0, "ED": 0.0, "EC": 0.0, "ER": 0.0}
      f = open("logs/sim_traces_" + ode_n + "_" + app_n + '.txt')
      summary_flag = False
      
      for line in f.readlines ():
        if not summary_flag:
          matched = re.search("After " + samples + " samples, average is (\d+\.\d+) QoS violations", line)
          
          if matched:
            summary_flag = True

        else:
          matched = re.search("Constraint violation distribution \(percentage\): {'(ED[^']*'): (\d+\.\d+), '(EC[^']*'): (\d+\.\d+)," + \
            " '(ER[^']*'): (\d+\.\d+), '(CD[^']*'): (\d+\.\d+), '(MD[^']*'): (\d+\.\d+)}", line)

          if matched:
            result[ode_n][app_n]['ED'] = float (matched.group (2))
            result[ode_n][app_n]['EC'] = float (matched.group (4))
            result[ode_n][app_n]['ER'] = float (matched.group (6))
            result[ode_n][app_n]['CD'] = float (matched.group (8))
            result[ode_n][app_n]['MD'] = float (matched.group (10))

  # print ('Constraint violation distribution: ' + str (result))

  for app_n in app_names:
    print (app_n + " constraint violations (in percentages)")

    for ode_n in ode_names:
      print (ode_n + ": " + str (result[ode_n][app_n]))

    print ()


def plot_average_qos_viols (regex, title):
  app_n = [MobApps.NAVIAR, MobApps.MOBIAR, MobApps.INTRASAFED]
  x = np.arange (len (app_n))
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
  yerr_ode = {"FRESCO": 0.0, "SMT": 0.0, "SQ": 0.0, "MDP": 0.0}
  result = dict ()
  # flag to detect when final part of result log will be parsed 
  # for summarizing overall task failure rate

  for ode_n in ode_names:
    result [ode_n] = list ()

    for app in app_n:
      f = open("logs/sim_traces_" + ode_n + "_" + app + '.txt')

      for line in f.readlines ():
        matched = re.search(regex, line)

        if matched:
          result[ode_n].append (float (matched.group (1)))
          yerr_ode[ode_n] = float (matched.group (3))

  # print (result)
  plt.rcParams.update({'font.size': 16})
  ax = plt.subplot(111)
  ax.bar(x - 0.2, result['FRESCO'], yerr = yerr_ode['FRESCO'],width = 0.1, color = 'red', \
    align = 'center', label = 'FRESCO')
  ax.bar(x - 0.1, result['SMT'], yerr = yerr_ode['SMT'], width = 0.1, color = 'green', \
    align = 'center', label = 'SMT')
  ax.bar(x + 0, result['SQ'], yerr = yerr_ode['SQ'], width = 0.1, color = 'yellow', \
    align = 'center', label = 'SQ')
  ax.bar(x + 0.1, result['MDP'], yerr = yerr_ode['MDP'], width = 0.1, color = 'purple', \
    align = 'center', label = 'MDP')

  plt.ylabel(title)
  plt.xlabel("Mobile applications")
  plt.xticks(x, app_n, fontsize = 16)
  # plt.legend()
  plt.tight_layout ()
  plt.show()


def plot_average_constr_viols (regex, title, samples):

  app_n = [MobApps.NAVIAR, MobApps.MOBIAR, MobApps.INTRASAFED]
  x = np.arange (len (app_n))
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
  result = dict ()
  # flag to detect when final part of result log will be parsed 
  # for summarizing overall task failure rate
  
  for ode_n in ode_names:
    result [ode_n] = list ()

    for app in app_n:
      summary_flag = False
      f = open("logs/sim_traces_" + ode_n + "_" + app + '.txt')

      for line in f.readlines ():
        if not summary_flag:
          matched = re.search ("After " + samples + " samples, average is (\d+\.\d+) QoS violations", line)
          
          if matched:
            summary_flag = True

        else:
          matched = re.search(regex, line)

          if matched:
            result[ode_n].append (float (matched.group (1)))

  print (result)
  plt.rcParams.update({'font.size': 16})
  ax = plt.subplot(111)
  ax.bar(x - 0.2, result['FRESCO'], width = 0.1, color = 'red', \
    align = 'center', label = 'FRESCO')
  ax.bar(x - 0.1, result['SMT'], width = 0.1, color = 'green', \
    align = 'center', label = 'SMT')
  ax.bar(x + 0, result['SQ'], width = 0.1, color = 'yellow', \
    align = 'center', label = 'SQ')
  ax.bar(x + 0.1, result['MDP'], width = 0.1, color = 'purple', \
    align = 'center', label = 'MDP')

  plt.ylabel(title)
  plt.xlabel("Mobile applications")
  plt.xticks(x, app_n, fontsize = 16)
  plt.legend()
  plt.show()


def plot_objective_with_mal (regex_exp, y_axis_title, show):

  app_n = MobApps.NAVIAR
  mal_scenarios = ["MAL1/5", "MAL2/5a", "MAL2/5b", "MAL2/5c"]
  x = np.arange(len(mal_scenarios))
  ode_names = ["FRESCO", "SMT", "SQ", "MDP"]
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
  ax.bar(x - 0.2, result['FRESCO'], width = 0.1, color = 'red', \
    align = 'center', label = 'FRESCO')
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


samples = sys.argv[1]
# overhead_plot ()
plot_objective ("After " + samples + " samples, average is (\d+\.\d+) s(.*) std: (\d+\.\d+)(.*)", 'Response time (seconds)', True)
plot_objective ("After " + samples + " samples, average is (\d+\.\d+) % of energy remains(.*) std: (\d+\.\d+)(.*)", "Battery lifetime (%)", False)
plot_objective ("After " + samples +" samples, average is (\d+\.\d+) monetary units(.*) std: (\d+\.\d+)(.*)", "Monetary units", False)
# print_constraint_violation_distribution ()
plot_offloading_distributions (samples)
# regex = "Average constraint violation rate \(percentage\) is (\d+\.\d+)(.*)"
# plot_average_constr_viols (regex, "Constraint violation rate (%)", samples)
# regex = "After " + samples + " samples, average is (\d+\.\d+) % QoS violation rate(.*) std: (\d+\.\d+)(.*)"
# plot_average_qos_viols (regex, "QoS violation rate (%)")