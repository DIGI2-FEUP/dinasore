import numpy as np
import time
import paho.mqtt.client as mqtt

class WRITE_MQTT:

    def schedule(self, event_name, event_value, topic, client, message):

        if event_name == 'INIT':
            # make publish
            return [None, None, None]

        if event_name == 'RUN':
            self.topic = topic
            self.client = client
            self.message = message

            self.client.publish(self.topic,str(self.message))

            return [None, None,
                    self.message]
