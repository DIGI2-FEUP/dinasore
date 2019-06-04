

class PressureSwitch:

    def __init__(self):
        self.pressure_1 = 0
        self.pressure_2 = 0
        self.cal_result = False

    def schedule(self, event_name, event_value):
        if event_name == 'Init':
            print('initialization')
            return [event_value, None, None, self.pressure_1, self.pressure_2, self.cal_result]

        elif event_name == 'Read':
            print('read temperature')
            self.pressure_1 += 1
            self.pressure_2 += 2
            return [None, event_value, None, self.pressure_1, self.pressure_2, self.cal_result]

        elif event_name == 'Calibrate':
            print('calibration')
            self.cal_result = True
            self.pressure_1 += 3
            self.pressure_2 += 4
            return [None, None, event_value, self.pressure_1, self.pressure_2, self.cal_result]
