

class Thermometer:

    def __init__(self):
        self.temperature = 0
        self.cal_result = False

    def schedule(self, event_name, event_value):
        if event_name == 'Init':
            print('initialization')
            return [event_value, None, None, self.temperature, self.cal_result]

        elif event_name == 'Read':
            print('read temperature')
            self.temperature += 1
            return [None, event_value, None, self.temperature, self.cal_result]

        elif event_name == 'Calibrate':
            print('calibration')
            self.cal_result = True
            return [None, None, event_value, self.temperature, self.cal_result]

