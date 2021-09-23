import numpy as np
import time
import paho.mqtt.client as mqtt

class MERGE:

    def schedule(self, event_name, event_value, str1, str2, merger):

        if event_name == 'INIT':
            # initiate any default simulation parameters
            self.counter = 0

            return [None, None,
                    None]

        elif event_name == 'RUN':

            return [None, event_value,
                    "{0}{1}{2}".format(str1,merger,str2)]
