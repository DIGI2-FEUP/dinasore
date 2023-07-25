from threading import Event
from paho.mqtt.client import Client
import json


class SharedResources:

    def __init__(self):
        self.client = None
        self.topic = None
        self.message_payload = None
        self.new_message = Event()

    def connect(self, host, port):
        self.client = Client()

        def on_message(client, userdata, message):
            # print('new message: {0}\ntopic: {1}'.format(message.payload, message.topic))
            self.topic = message.topic
            self.message_payload = message.payload
            self.new_message.set()

        self.client.on_message = on_message
        self.client.connect(host, port)
        self.client.loop_start()


class MQTT_SUBSCRIBER_2:
    resources = SharedResources()

    def __init__(self):
        self.resources.new_message.clear()
        self.stop = Event()

    def schedule(self, event_name, event_value, topic, host, port, value_name_1, value_name_2):
        if event_name == 'INIT':
            self.resources.connect(host, port)
            self.resources.client.subscribe(topic)
            return [event_value, None, 0.0, 0.0]

        elif event_name == 'READ':
            # wait for new messages
            while not self.stop.is_set():
                self.resources.new_message.wait()

                # checks if is the right topic
                if self.resources.topic == topic and self.resources.message_payload is not None:
                    # process each message
                    msg = self.resources.message_payload.decode('utf-8')
                    payload_json = json.loads(msg)
                    value_1 = float(payload_json[value_name_1])
                    value_2 = float(payload_json[value_name_2])
                    # otherwise clears the new message event
                    self.resources.new_message.clear()
                    return [None, event_value, value_1, value_2]

    def __del__(self):
        self.stop.set()
        self.resources.new_message.clear()
        self.resources.client.disconnect()
