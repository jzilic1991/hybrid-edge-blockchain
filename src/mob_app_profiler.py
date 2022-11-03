import json
import numpy as np

from mobile_app import MobileApplication
from util import MobApps




class MobileAppProfiler:

    def __init__ (self):

        self._mobile_apps = self.__instantiate_mobile_apps \
            (json.load (open ('data/applications.json')))

    
    def deploy_random_mobile_app (cls):
        
        choice = np.random.choice(len(cls._mobile_apps), 1, \
            p = [app.get_prob() for app in cls._mobile_apps])[0]

        return cls._mobile_apps[choice]

    

    def __instantiate_mobile_apps (cls, data):
        
        mob_apps = list ()
        app_names = (MobApps.ANTIVIRUS, MobApps.GPS_NAVIGATOR, \
                MobApps.CHESS, MobApps.FACERECOGNIZER, MobApps.FACEBOOK)

        # iterate through applications
        for app_name in app_names:
            mob_apps.append (MobileApplication \
                (app_name, data[app_name]))

        return mob_apps


a = MobileAppProfiler ()