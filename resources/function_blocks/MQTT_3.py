from paho.mqtt.client import Client
from threading import Event
from threading import Thread


class MQTT_3:

    def __init__(self):
        self.values = [None, None, None]
        self.event = Event()
        self.client = None

    def schedule(self, event_name, event_value, topic_0, topic_1, topic_2, host, port):
        if event_name == 'INIT':
            return self.connect_client(event_value, topic_0, topic_1, topic_2, host, port)

        elif event_name == 'REQ':
            return self.read_measures(event_value)

    def connect_client(self, event_value, topic_0, topic_1, topic_2, host, port):

        class MQTTClient(Thread):

            def __init__(self, values, event):
                Thread.__init__(self)
                self.values = values
                self.event = event

            def run(self):
                client = Client()

                def on_message(client, userdata, message):
                    print('new message: {0}'.format(message))
                    if message.topic == topic_0:
                        self.values[0] = message.payload
                    elif message.topic == topic_1:
                        self.values[1] = message.payload
                    elif message.topic == topic_2:
                        self.values[2] = message.payload
                    if (self.values[0] is not None) and (self.values[1] is not None) and (self.values[2] is not None):
                        self.event.set()

                client.on_message = on_message
                client.connect(host, port)
                client.subscribe(topic_0)
                client.subscribe(topic_1)
                client.subscribe(topic_2)
                client.loop_forever()

        MQTTClient(self.values, self.event).start()

        return [event_value, None, 0.0, 0.0, 0.0]

    def read_measures(self, event_value):
        self.event.wait()
        value_0 = self.values[0]
        value_1 = self.values[1]
        value_2 = self.values[2]
        self.values[0] = None
        self.values[1] = None
        self.values[2] = None
        self.event.clear()
        return [None, event_value, value_0, value_1, value_2]


c = MQTT_3()
c.connect_client(1, '/t_0', '/t_1', '/t_2', 'localhost', 1883)
v = c.read_measures(1)
print(v)
v = c.read_measures(1)
print(v)
# client.send_measure(1, 0.0)
