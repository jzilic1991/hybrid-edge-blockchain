import numpy as np


class Stats:

    def __init__(self):
         
         self._rsp_time_samp = list ()   # of scalars
         self._e_consum_samp = list ()   # of scalars
         self._price_samp = list ()      # of scalars
         self._off_dist_samp = list ()   # of dicts per offloading site key
         self._off_fail_samp = list ()   # of scalars
         self._mal_beh_samp = list ()    # of dicts per offloading site key


    def print_avg_rsp_time (cls): 
        
        print ("After " + str (len (cls._rsp_time_samp)) + " executions, average is " + \
            str (round (np.mean(cls._rsp_time_samp), 2)) + " s")


    def print_avg_e_consum (cls):
        
        print ("After " + str (len (cls._e_consum_samp)) + " executions, average is " + \
            str (round (np.mean(cls._e_consum_samp), 2)) + " J")


    def print_avg_prices (cls):
        
        print ("After " + str (len (cls._price_samp)) + " executions, average is " + \
            str (round (np.mean(cls._price_samp), 2)) + " monetary units")


    def print_all (cls):

        cls.print_avg_rsp_time ()
        cls.print_avg_e_consum ()
        cls.print_avg_prices ()


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


    def add_off_dist (cls, off_dist_samp):
        
        cls._off_dist_samp.append (off_dist_samp)


    def add_off_fail_fr (cls, off_fail_fr):
        
        cls._off_fail_samp.append (off_fail_fr)


    def add_mal_beh (cls, mal_beh_samp):
        
        cls._mal_beh_samp.append (mal_beh_samp)


    def reset (cls):
        
        cls._rsp_time_samp = list ()   # of scalars
        cls._e_consum_samp = list ()   # of scalars
        cls._price_samp = list ()      # of scalars
        cls._off_dist_samp = list ()   # of dicts per offloading site key
        cls._off_fail_samp = list ()   # of scalars
        cls._mal_beh_samp = list ()    # of dicts per offloading site key