import numpy as np
import time
import paho.mqtt.client as mqtt
from threading import Event
import queue
import asyncio

class INIT_MQTT_ASYNC:

    def on_messages(self, client, userdata, message):
        #print("message received ", str(message.payload.decode("utf-8")))
        #print("message topic=", message.topic)

        #time.sleep(0.1)

        self.queue.append([message.topic,str(message.payload.decode("utf-8"))])
        print("INIT message: " , str(message.payload.decode("utf-8")) , "queue len: ", len(self.queue))

        #self.messages = dict()
        #self.messages[message.topic] = str(message.payload.decode("utf-8"))
        #self.new_message.set()

    def connect(self):

        if (self.address is not None) and (self.port is not None) and (self.timeout is not None):

            self.client = mqtt.Client()
            self.client.connect(self.address, self.port, self.timeout)

            #################################
            ## All necessary declarations
            self.client.on_message = self.on_messages
            self.client.loop_start()

            self.messages = dict()

            return 10
        else:
            print("Please define address, port and timeout")
            return 9

    def schedule(self, event_name, event_value, address, port, timeout):

        if event_name == 'INIT':

            self.counter = 1
            self.read_counter = 0
            self.queue = []

            # make the first connection
            self.address = str(address)
            self.port = int(port)
            self.timeout = int(timeout)

            self.new_message = Event()
            self.new_message.clear()

            if self.connect() == 10: # everything is fine
                return [None, event_value, event_value, None,
                        self.client, None]
            else:
                return [None, None, None, None,
                        None, None]

        elif event_name == 'READ':

            time.sleep(0.1)

            '''
            print("INIT entrei read len(self.queue): ", len(self.queue))
            
            if len(self.queue) == 0:
                ## wait for new message
                self.new_message.wait()
                self.new_message.clear()

                print("INIT len(self.queue) after wait:", len(self.queue))
                self.read_counter += 1
                print("INIT self.read_counter: ", self.read_counter)
            '''

            if len(self.queue) > 0:
                return [None, event_value, None, event_value,
                        None, self.queue.pop()]
            else:
                return [None, event_value, None, None,
                        None, None]

            '''
            else:
                if len(self.queue) > 0:
                    return [None, event_value, None, event_value,
                            None, self.queue.pop()]
                else:
                    return [None, None, None, None,
                            None, None]
            '''