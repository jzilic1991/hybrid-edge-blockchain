import numpy as np

from util import Settings

class Stats:

    def __init__(self):
         self._rsp_time_samp = list ()   # of scalars
         self._e_consum_samp = list ()   # of scalars
         self._price_samp = list ()      # of scalars
         self._bl_samp = list ()         # of scalars
         self._mal_beh_samp = list ()    # of dicts per offloading site key
         self._qos_viol_samp = list ()
         self._score_samp = list ()
    

    def get_sum_e_consum(self):
        return sum(self._e_consum_samp)

    def get_sum_res_pr(self):
        return sum(self._price_samp)

    def get_avg_rsp_time_value(self):
        if not self._rsp_time_samp:
            return 0.0
        return round(np.mean(self._rsp_time_samp), 4)
    
    def get_avg_e_consum_value(self):
        if not self._e_consum_samp:
            return 0.0
        return round(np.mean(self._e_consum_samp), 4)

    def get_avg_res_pr_value(self):
        if not self._price_samp:
            return 0.0
        return round(np.mean(self._price_samp), 4)

    def get_avg_qos_viol_value(self):
        if not self._qos_viol_samp:
            return 0.0
        return round(np.mean(self._qos_viol_samp), 4)

    def get_avg_score_value(self):
        if not self._score_samp:
            return 0.0
        return round(np.mean(self._score_samp), 4)


    def get_avg_qos_viol (self):
        if not self._qos_viol_samp:
            return "Average QoS violation rate: 0.000 %"
        return (
            f"After {len(self._qos_viol_samp)} samples, average is {np.mean(self._qos_viol_samp):.3f} % QoS violation rate "
            f"(min: {np.min(self._qos_viol_samp):.3f}, max: {np.max(self._qos_viol_samp):.3f}, "
            f"var: {np.var(self._qos_viol_samp):.3f}, std: {np.std(self._qos_viol_samp):.3f}, "
            f"median: {np.median(self._qos_viol_samp):.3f})"
        )

    def get_avg_score (self):
        if not self._score_samp:
            return "Average score: 0.000"
        return (
            f"After {len(self._score_samp)} samples, average is {np.mean(self._score_samp):.3f} score "
            f"(min: {np.min(self._score_samp):.3f}, max: {np.max(self._score_samp):.3f}, "
            f"var: {np.var(self._score_samp):.3f}, std: {np.std(self._score_samp):.3f}, "
            f"median: {np.median(self._score_samp):.3f})"
        )

    def get_avg_rsp_time (self): 
        if not self._rsp_time_samp:
            return "Average response time: 0.000 s"
        return (
            f"After {len(self._rsp_time_samp)} samples, average is {np.mean(self._rsp_time_samp):.3f} s "
            f"(min: {np.min(self._rsp_time_samp):.3f}, max: {np.max(self._rsp_time_samp):.3f}, "
            f"var: {np.var(self._rsp_time_samp):.3f}, std: {np.std(self._rsp_time_samp):.3f}, "
            f"median: {np.median(self._rsp_time_samp):.3f})"
        )

    def get_avg_e_consum (self):
        if not self._e_consum_samp:
            return "Average energy consumption: 0.000 J"
        return (
            f"After {len(self._e_consum_samp)} samples, average is {np.mean(self._e_consum_samp):.3f} J "
            f"(min: {np.min(self._e_consum_samp):.3f}, max: {np.max(self._e_consum_samp):.3f}, "
            f"var: {np.var(self._e_consum_samp):.3f}, std: {np.std(self._e_consum_samp):.3f}, "
            f"median: {np.median(self._e_consum_samp):.3f})"
        )

    def get_avg_prices (self):
        if not self._price_samp:
            return "Average price: 0.000 monetary units"
        return (
            f"After {len(self._price_samp)} samples, average is {np.mean(self._price_samp):.3f} monetary units "
            f"(min: {np.min(self._price_samp):.3f}, max: {np.max(self._price_samp):.3f}, "
            f"var: {np.var(self._price_samp):.3f}, std: {np.std(self._price_samp):.3f}, "
            f"median: {np.median(self._price_samp):.3f})"
        )

    def get_avg_bl (self):
        if not self._bl_samp:
            return "Average battery level: 0.000 %"
        return (
            f"After {len(self._bl_samp)} samples, average is {np.mean(self._bl_samp):.3f} % of energy remains "
            f"(min: {np.min(self._bl_samp):.3f}, max: {np.max(self._bl_samp):.3f}, "
            f"var: {np.var(self._bl_samp):.3f}, std: {np.std(self._bl_samp):.3f}, "
            f"median: {np.median(self._bl_samp):.3f})"
        )

    def get_off_dist_dict(cls, cells):
        """Return offloading distribution as a dictionary of percentages."""

        result = dict()
        off_dist_samp = dict()

        for cell_name, cell in cells.items():
            for site, samples in cell.get_off_dist_samp().items():
                if site not in off_dist_samp:
                    off_dist_samp[site] = list()

                off_dist_samp[site] += samples

        for key, val in off_dist_samp.items():
            result[key] = round(sum(val) / len(val), 2)

        rel_result = dict()
        all_offloads = sum(result.values())
        if all_offloads == 0:
            return {key: 0 for key in result}

        for key, val in result.items():
            rel_result[key] = round((val / all_offloads) * 100, 2)

        return rel_result

    def get_avg_off_dist (cls, cells):
        dist = cls.get_off_dist_dict(cells)
        return ("Offloading distribution (percentage): " + str(dist))


    def get_avg_off_fail (cls, cells):

        off_fail = list ()
        off_fail_samp = dict ()
        off_dist_samp = dict ()

        for cell_name, cell in cells.items ():
            for site, samples in cell.get_off_fail_samp().items ():
                if not site in off_fail_samp:
                    off_fail_samp[site] = list ()
                    
                off_fail_samp[site] += samples

            for site, samples in cell.get_off_dist_samp().items ():
                if not site in off_dist_samp:
                    off_dist_samp[site] = list ()
                    
                off_dist_samp[site] += samples

        for key, _ in off_fail_samp.items ():
            for i in range (len (off_fail_samp[key])):
                if off_dist_samp[key][i] != 0:
                    off_fail.append (round (off_fail_samp[key][i] / off_dist_samp[key][i] \
                        * 100, 3))
                else:
                    off_fail.append (0.0)

        if len (off_fail) == 0:
          return "Average task failure rate is 0.0 %"

        return "Average task failure rate is " + \
            str (round (sum (off_fail) / len (off_fail), 3)) + " %"


    def get_avg_constr_viol (cls, cells):

        constr_viol = list ()

        for i in range (Settings.SAMPLES):
          off_dist_cnt = 0
          constr_viol_cnt = 0

          # per cell
          for cell_name, cell in cells.items ():
            #print (cell.get_constr_viol_samp ())
            #print (cell.get_off_dist_samp ())
            
            # per offloading site
            for site_name, constr_viol_samp in cell.get_constr_viol_samp().items ():
              off_dist_samp = cell.get_off_dist_samp ()
              off_dist_cnt += off_dist_samp[site_name][i]
              constr_viol_cnt += constr_viol_samp[i]

          # if no offloading attempts in the cell (e.g. last cell in the app execution sample)
          if off_dist_cnt == 0:
            constr_viol.append (0.0)
            continue

          constr_viol.append (round (constr_viol_cnt / off_dist_cnt * 100, 3))

        if len (constr_viol) == 0:
          return "Average constraint violation rate is 0.0 %"

        return "Average constraint violation rate is " + \
            str (round (sum (constr_viol) / len (constr_viol), 3)) + " %"


    def get_avg_off_fail_dist (cls, cells):

        off_fail_samp = dict ()
        off_dist_samp = dict ()

        for cell_name, cell in cells.items ():

            for site, samples in cell.get_off_fail_samp().items ():

                if not site in off_fail_samp:

                    off_fail_samp[site] = list ()
                    
                off_fail_samp[site] += samples

            for site, samples in cell.get_off_dist_samp().items ():

                if not site in off_dist_samp:

                    off_dist_samp[site] = list ()
                    
                off_dist_samp[site] += samples

        off_fail = dict ()
        for key, val in off_fail_samp.items ():
            
            off_fail[key] = round (sum (val) / len (val), 3)

        off_dist = dict ()
        for key, val in off_dist_samp.items ():
            
            off_dist[key] = round (sum (val) / len (val), 3)

        result = dict ()
        for key in off_fail_samp.keys ():
            
            if off_dist[key] != 0:

                result[key] = round ((off_fail[key] / off_dist[key]) * 100, 2)

            else:

                result[key] = 0

        return ("Offloading failure distribution (percentage): " + str (result))


    def get_avg_constr_viol_dist (cls, cells):

        constr_viol_samp = dict ()
        off_dist_samp = dict ()

        for cell_name, cell in cells.items ():
            for site, samples in cell.get_constr_viol_samp().items ():
                if not site in constr_viol_samp:
                    constr_viol_samp[site] = list ()
                    
                constr_viol_samp[site] += samples

            for site, samples in cell.get_off_dist_samp().items ():
                if not site in off_dist_samp:
                    off_dist_samp[site] = list ()
                    
                off_dist_samp[site] += samples

        constr_viol = dict ()
        for key, val in constr_viol_samp.items ():
            constr_viol[key] = round (sum (val) / len (val), 3)

        off_dist = dict ()
        for key, val in off_dist_samp.items ():
            off_dist[key] = round (sum (val) / len (val), 3)

        result = dict ()
        for key in constr_viol_samp.keys ():
            if off_dist[key] != 0:
                result[key] = round ((constr_viol[key] / off_dist[key]) * 100, 2)

            else:
                result[key] = 0

        return ("Constraint violation distribution (percentage): " + str (result))


    def get_all (self):
        return "\n".join([
            self.get_avg_rsp_time(),
            self.get_avg_e_consum(),
            self.get_avg_prices(),
            self.get_avg_bl(),
            self.get_avg_qos_viol(),
            self.get_avg_score()
        ])

    def get_cell_stats (cls, cell_stats):

        return cls.get_avg_off_dist (cell_stats) + "\n" + cls.get_avg_off_fail_dist (cell_stats) + "\n" + \
            cls.get_avg_off_fail (cell_stats) + "\n" + cls.get_avg_constr_viol_dist (cell_stats) + "\n"+ \
            cls.get_avg_constr_viol (cell_stats) + "\n"


    def print_off_dist (cls):
        
        print (cls._off_dist_samp)


    def print_off_fail_fr (cls):
        
        print (cls._off_fail_samp)


    def print_mal_beh (cls):
        
        print (cls._mal_beh_samp)


    def add_rsp_time (cls, rsp_time_samp):
        
        cls._rsp_time_samp.append (rsp_time_samp)


    def add_e_consum (cls, e_consum_samp):
        
        cls._e_consum_samp.append (e_consum_samp)


    def add_res_pr (cls, price_samp):

        cls._price_samp.append (price_samp)


    def add_bl (cls, bl_samp):

        cls._bl_samp.append (bl_samp)


    def add_qos_viol (cls, qos_viol):

        cls._qos_viol_samp.append (qos_viol)

    def add_score (cls, score):

        cls._score_samp.append (score)


    # def add_off_dist (cls, off_dist_samp):
    #     for key, val in off_dist_samp.items ():
    #         if key in cls._off_dist_samp.keys ():
    #             cls._off_dist_samp[key].append (val)
    #         else:
    #             cls._off_dist_samp[key] = [val]


    # def add_off_fail (cls, off_fail_samp):
    #     for key, val in off_fail_samp.items ():
    #         if key in cls._off_fail_samp.keys ():
    #             cls._off_fail_samp[key].append (val)
    #         else:
    #             cls._off_fail_samp[key] = [val]


    def add_mal_beh (cls, mal_beh_samp):
        
        cls._mal_beh_samp.append (mal_beh_samp)


    def reset (cls):

        cls._rsp_time_samp = list ()   # of scalars
        cls._e_consum_samp = list ()   # of scalars
        cls._price_samp = list ()      # of scalars
        cls._bl_samp = list ()        # of scalars
        cls._mal_beh_samp = list ()    # of dicts per offloading site key
        cls._qos_viol_samp = list ()
        cls._score_samp = list ()
