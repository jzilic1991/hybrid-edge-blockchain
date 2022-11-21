import numpy as np


class Stats:

    def __init__(self):
         
         self._rsp_time_samp = list ()   # of scalars
         self._e_consum_samp = list ()   # of scalars
         self._price_samp = list ()      # of scalars
         self._bl_samp = list ()         # of scalars
         self._off_dist_samp = dict ()   # of dicts per offloading site key
         self._off_fail_samp = dict ()   # of scalars
         self._mal_beh_samp = list ()    # of dicts per offloading site key


    def get_avg_rsp_time (cls): 
        
        return ("After " + str (len (cls._rsp_time_samp)) + " samples, average is " + \
            str (round (np.mean(cls._rsp_time_samp), 2)) + " s")


    def get_avg_e_consum (cls):
        
        return ("After " + str (len (cls._e_consum_samp)) + " samples, average is " + \
            str (round (np.mean(cls._e_consum_samp), 2)) + " J")


    def get_avg_prices (cls):
        
        return ("After " + str (len (cls._price_samp)) + " samples, average is " + \
            str (round (np.mean(cls._price_samp), 2)) + " monetary units")


    def get_avg_bl (cls):

        return ("After " + str (len (cls._bl_samp)) + " samples, average is " + \
            str (round (np.mean(cls._bl_samp), 2)) + " % of energy remains")


    def get_avg_off_dist (cls):

        result = dict ()

        for key, val in cls._off_dist_samp.items ():
            
            result[key] = sum (val) / len (val)

        rel_result = dict ()
        all_offloads = sum (result.values ())
        for key, val in result.items ():

            rel_result[key] = round (val / all_offloads, 2) * 100

        return ("Offloading distribution (percentage): " + str (rel_result))


    def get_avg_off_fail (cls):

        off_fail = dict ()

        for key, val in cls._off_fail_samp.items ():
            
            off_fail[key] = sum (val) / len (val)

        off_dist = dict ()

        for key, val in cls._off_dist_samp.items ():
            
            off_dist[key] = sum (val) / len (val)

        result = dict ()

        for key in cls._off_fail_samp.keys ():
            
            if off_dist[key] != 0:

                result[key] = (off_fail[key] / off_dist[key]) * 100

            else:

                result[key] = 0

        return ("Offloading failure distribution (percentage): " + str (result))


    def get_all (cls):

        return cls.get_avg_rsp_time () + '\n' + cls.get_avg_e_consum () + '\n' + \
            cls.get_avg_prices () + '\n' + cls.get_avg_bl () + '\n' + cls.get_avg_off_dist () + '\n' + \
            cls.get_avg_off_fail ()


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


    def add_off_dist (cls, off_dist_samp):
        
        for key, val in off_dist_samp.items ():

            if key in cls._off_dist_samp.keys ():

                cls._off_dist_samp[key].append (val)

            else:

                cls._off_dist_samp[key] = [val]


    def add_off_fail (cls, off_fail_samp):
        
        for key, val in off_fail_samp.items ():

            if key in cls._off_fail_samp.keys ():

                cls._off_fail_samp[key].append (val)

            else:

                cls._off_fail_samp[key] = [val]


    def add_mal_beh (cls, mal_beh_samp):
        
        cls._mal_beh_samp.append (mal_beh_samp)


    def reset (cls):
        
        cls._rsp_time_samp = list ()   # of scalars
        cls._e_consum_samp = list ()   # of scalars
        cls._price_samp = list ()      # of scalars
        cls._bl_samp = list ()        # of scalars
        cls._off_dist_samp = dict ()   # of dicts per offloading site key
        cls._off_fail_samp = dict ()   # of scalars
        cls._mal_beh_samp = list ()    # of dicts per offloading site key