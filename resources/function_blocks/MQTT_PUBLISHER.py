from paho.mqtt.client import Client
import json


class MQTT_PUBLISHER:

    def __init__(self):
        self.client = Client()

    def schedule(self, event_name, event_value, topic, host, port, value_name, value):
        if event_name == 'INIT':
            # connects to the broker
            self.client.connect(host, port)
            return [event_value, None]

        elif event_name == 'RUN':
            message_dict = {value_name: str(value)}
            message = json.dumps(message_dict)
            self.client.publish(topic, message)
            return [None, event_value]

    def __del__(self):
        self.client.disconnect()
