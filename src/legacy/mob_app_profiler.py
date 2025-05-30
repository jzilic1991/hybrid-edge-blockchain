import json
import numpy as np

from mobile_app import MobileApplication
from util import MobApps


class MobileAppProfiler:

    def __init__ (self):

        self._mob_apps = self.__create_mob_apps \
            (json.load (open ('data/applications.json')))

    
    def dep_rand_mob_app (cls):
        
        choice = np.random.choice(len(cls._mob_apps), 1, \
            p = [MobApps.PROBS[app.get_name ()] for app in cls._mob_apps])[0]

        return cls._mob_apps[choice]


    def dep_app (cls, app_name):

        for mob_app in cls._mob_apps:

            if mob_app.get_name () == app_name:

                return mob_app
    

    def __create_mob_apps (cls, data):
        
        mob_apps = list ()
        #app_names = (MobApps.ANTIVIRUS, MobApps.GPS_NAVIGATOR, \
        #        MobApps.CHESS, MobApps.FACERECOGNIZER, MobApps.FACEBOOK)
        app_names = (MobApps.INTRASAFED, MobApps.MOBIAR, MobApps.NAVIAR)

        # iterate through applications
        for app_name in app_names:
            
            mob_apps.append (MobileApplication (app_name, data[app_name]))

        return mob_apps