from influxdb import InfluxDBClient


class INFLUX_SERVICE:

    def __init__(self):
        self.client = None

    def schedule(self, event_name, event_value,
                 temperature, measurement_name, host, port, user, password, db_name):

        if event_name == 'INIT':
            return self.connect_client(event_value, host, port, user, password, db_name)

        elif event_name == 'RUN':
            return self.send_measure(event_value, temperature, measurement_name)

    def connect_client(self, event_value, host, port, user, password, db_name):
        self.client = InfluxDBClient(host=host,
                                     port=port,
                                     username=user,
                                     password=password,
                                     database=db_name)

        return [event_value, None]

    def send_measure(self, event_value, temperature, measurement_name):
        json_body = [
            {
                "measurement": measurement_name,
                "tags": {},
                "fields": {
                    "temperature": float(temperature)
                }
            }
        ]
        self.client.write_points(json_body)
        return [None, event_value]

# client = INFLUX_CLIENT()
# client.connect_client(1, '192.168.0.102', 8086, 'fucoli', 'humidity', 'fucolidb')
# client.send_measure(1, 0.0)

# client1 = INFLUX_CLIENT()
# client1.connect_client(1, '192.168.0.102', 8086, 'fucoli', 'humidity', 'fucolidb')
