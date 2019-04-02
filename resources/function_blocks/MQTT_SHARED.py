from threading import Event
from paho.mqtt.client import Client
import json


class SharedResources:

    def __init__(self):
        self.client = Client()
        self.topic = None
        self.message_payload = None
        self.new_message = Event()

    def connect(self, host, port):

        def on_message(client, userdata, message):
            print('new message: {0}\ntopic: {1}'.format(message.payload, message.topic))
            self.topic = message.topic
            self.message_payload = message.payload
            self.new_message.set()

        self.client.on_message = on_message
        self.client.connect(host, port)
        self.client.loop_start()


class MQTT_SHARED:
    resources = SharedResources()

    def schedule(self, event_name, event_value, topic, host, port):
        if event_name == 'INIT':
            self.resources.connect(host, port)
            return [event_value, None, None, 0.0, 0.0]

        elif event_name == 'SUBS':
            self.resources.client.subscribe(topic)
            return [None, event_value, None, 0.0, 0.0]

        elif event_name == 'READ':
            self.resources.new_message.wait()

            if self.resources.topic == topic:
                msg = self.resources.message_payload.decode('utf-8')
                payload_json = json.loads(msg)
                self.resources.new_message.clear()
                humidity = payload_json['S1TH']['Humidity']
                temperature = payload_json['S1TH']['Temperature']
                return [None, None, event_value, humidity, temperature]
            else:
                self.schedule('READ', event_value, topic, host, port)

        elif event_name == 'STOP':
            self.resources.client.disconnect()
            return [None, None, None, 0.0, 0.0]


c = MQTT_SHARED()
c.schedule('INIT', 1, 'Fucoli/ISQsensor1/sensor', 'localhost', 1883)
c.schedule('SUBS', 1, 'Fucoli/ISQsensor1/sensor', 'localhost', 1883)
v = c.schedule('READ', 1, 'Fucoli/ISQsensor1/sensor', 'localhost', 1883)
print(v)
v = c.schedule('READ', 1, 'Fucoli/ISQsensor1/sensor', 'localhost', 1883)
print(v)
# {"Time":"2019-04-01T17:46:26", "S1TH":{"Temperature":20.7, "Humidity":53.8},"TempUnit":"C"}
