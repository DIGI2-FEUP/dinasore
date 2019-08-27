from influxdb import InfluxDBClient


class INFLUX_DB:

    def __init__(self):
        self.client = None

    def schedule(self, event_name, event_value,
                 value, moving_average, measurement_name,
                 host, port, user, password, db_name):

        if event_name == 'INIT':
            return self.connect_client(event_value, host, port, user, password, db_name)

        elif event_name == 'RUN':
            return self.send_measure(event_value, value, moving_average, measurement_name)

    def connect_client(self, event_value, host, port, user, password, db_name):
        self.client = InfluxDBClient(host=host,
                                     port=port,
                                     username=user,
                                     password=password,
                                     database=db_name)
        # print('connect')
        return [event_value, None]

    def send_measure(self, event_value, value, moving_average, measurement_name):
        # print('send measure: ', value, moving_average)
        json_body = [
            {
                "measurement": measurement_name,
                "tags": {},
                "fields": {
                    "value": float(value),
                    "moving_average": float(moving_average)
                }
            }
        ]
        self.client.write_points(json_body)
        return [None, event_value]
