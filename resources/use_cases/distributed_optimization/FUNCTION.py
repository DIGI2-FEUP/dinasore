import numpy as np
import time
import paho.mqtt.client as mqtt


class FUNCTION:

    def schedule(self, event_name, event_value, value):

        if event_name == 'INIT':
            # initiate any default simulation parameters
            return [None, None, None]

        elif event_name == 'RUN':
            # Should wait for the handler
            return [None, event_value, 1/value]
