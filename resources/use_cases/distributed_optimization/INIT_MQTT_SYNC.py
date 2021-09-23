import numpy as np
import time
import paho.mqtt.client as mqtt

class INIT_MQTT_SYNC:

    def schedule(self, event_name, event_value, address, port, timeout):

        if event_name == 'INIT':
            # make the first connection
            self.counter = 0

            return [None, None, event_value, None,
                    "MQTT Client init", None]

        elif event_name == 'READ':
            # Should wait for the handler
            time.sleep(3)
            self.counter += 1


            return [None, event_value, None, event_value,
                    "MQTT Client {0}".format(self.counter), "Message {0}".format(self.counter)]
