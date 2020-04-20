

class TEST_DEVICE_SENSOR:

    def __init__(self):
        self.temperature = 0

    def schedule(self, event_name, event_value):
        if event_name == 'INIT':
            return [event_value, None, None, self.temperature, False]

        elif event_name == 'READ':
            # self.temperature += 1
            return [None, event_value, None, self.temperature, True]

        elif event_name == 'CALIBRATE':
            self.temperature = 23
            return [None, None, event_value, self.temperature, True]
