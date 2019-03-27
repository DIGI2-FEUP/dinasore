from influxdb import InfluxDBClient
import datetime


class INFLUX_CLIENT:

    def __init__(self):
        self.client = None

    def schedule(self, event_name, event_value, value, host, port, user, password, db_name):
        if event_name == 'INIT':
            return self.connect_client(event_value, host, port, user, password, db_name)

        elif event_name == 'REQ':
            return self.send_measure(event_value, value)

    def connect_client(self, event_value, host, port, user, password, db_name):
        self.client = InfluxDBClient(host=host,
                                     port=port,
                                     username=user,
                                     password=password,
                                     database=db_name)
        return [event_value, None]

    def send_measure(self, event_value, value):
        date = datetime.datetime.now()
        json_body = [
            {
                "measurement": "humidity",
                "tags": {
                    "sensor_type": "line",
                    "sensor_id": 0
                },
                "time": date,
                "fields": {
                    "percentage": value
                }
            }
        ]
        self.client.write_points(json_body)
        return [None, event_value]


client = INFLUX_CLIENT()
client.connect_client(1, '192.168.0.104', 8086, 'fucoli', 'humidity', 'fucolidb')
client.send_measure(1, 0.0)
