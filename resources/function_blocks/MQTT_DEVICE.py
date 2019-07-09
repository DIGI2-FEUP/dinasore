from threading import Event
from threading import Lock
from paho.mqtt.client import Client
import json


class SharedResources:

    def __init__(self):
        self.client = None
        self.topic = None
        self.message_payload = None
        self.new_message = Event()
        self.stop = Event()
        self.read_message = Lock()

    def connect(self, host, port):
        self.client = Client()

        def on_message(client, userdata, message):
            # print('new message: {0}\ntopic: {1}'.format(message.payload, message.topic))
            self.read_message.acquire()
            self.topic = message.topic
            self.message_payload = message.payload
            self.new_message.set()

        self.client.on_message = on_message
        self.client.connect(host, port)
        self.client.loop_start()


class MQTT_DEVICE:
    resources = SharedResources()

    def __init__(self):
        self.resources.new_message.clear()

    def schedule(self, event_name, event_value, topic, host, port):
        if event_name == 'INIT':
            self.resources.connect(host, port)
            self.resources.client.subscribe(topic)
            return [event_value, None, None, 0.0]

        elif event_name == 'READ':
            # wait for new messages
            while not self.resources.stop.is_set():
                self.resources.new_message.wait()

                # checks if is the right topic
                if self.resources.topic == topic and self.resources.message_payload is not None:
                    # process each message
                    msg = self.resources.message_payload.decode('utf-8')
                    payload_json = json.loads(msg)
                    value = payload_json['temperature_value']
                    # otherwise clears the new message event
                    self.resources.new_message.clear()
                    self.resources.read_message.release()
                    return [None, event_value, None, value]

                # otherwise clears the new message event
                # self.resources.new_message.clear()

        elif event_name == 'STOP':
            self.resources.stop.set()
            self.resources.read_message.release()
            self.resources.new_message.clear()
            self.resources.client.disconnect()
            return [None, None, event_value, 0.0]

    def __del__(self):
        self.resources.stop.set()
        self.resources.read_message.release()
        self.resources.new_message.clear()
        self.resources.client.disconnect()
