from influxdb import InfluxDBClient


class INFLUX_DB_2:

    def __init__(self):
        self.client = None

    def schedule(self, event_name, event_value,
                 host, port, user, password, db_name, measurement_name,
                 value_name_1, value_name_2, value_1, value_2):

        if event_name == 'INIT':
            self.client = InfluxDBClient(host=host,
                                         port=port,
                                         username=user,
                                         password=password,
                                         database=db_name)
            # print('connect')
            return [event_value, None]

        elif event_name == 'RUN':
            json_body = [
                {
                    "measurement": measurement_name,
                    "tags": {},
                    "fields": {
                        value_name_1: float(value_1),
                        value_name_2: float(value_2)
                    }
                }
            ]
            self.client.write_points(json_body)
            return [None, event_value]
