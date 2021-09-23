import numpy as np
import time
import paho.mqtt.client as mqtt

class READ_MQTT:

    def schedule(self, event_name, event_value, topic, client, message):

        if event_name == 'INIT':
            self.counter = 1
            return [None, None, None]

        elif event_name == 'RUN':
            self.topic = topic
            self.client = client
            self.past_message = None
            self.message = []

            self.client.subscribe(self.topic)

            return [None, None,
                    None]


        elif event_name == 'MESSAGE_I':
            # Should wait for the handler

            #self.message = message
            self.message.append(message)

            temp_pop = self.message.pop()

            ##########
            if self.topic not in temp_pop[0]:
                return [None, None,
                        None]
            else:
                print("READ sent message - topic: ", self.topic, ": ", message)
                #return [None, event_value, self.message[self.topic]]
                #return [None, event_value, self.message[1]]
                return [None, event_value,
                        temp_pop[1]]

            '''
            if self.past_message is None:
                return [None, event_value,
                        self.message[self.topic]]
            else:
                if self.past_message == self.message[self.topic]:
                    return [None, None,
                            None]
                else:
                    self.past_message = self.message[self.topic]
                    return [None, event_value,
                            self.past_message]
            '''


