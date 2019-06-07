

class SprinklingTime:

    def __init__(self):
        self.PowerWashI = 0
        self.CSE = 0
        self.cal_result = False

    def schedule(self, event_name, event_value):
        if event_name == 'Init':
            # print('initialization')
            return [event_value, None, None, self.PowerWashI, self.CSE, self.cal_result]

        elif event_name == 'Read':
            # print('read temperature')
            self.PowerWashI += 1
            self.CSE += 2
            return [None, event_value, None, self.PowerWashI, self.CSE, self.cal_result]

        elif event_name == 'Calibrate':
            # print('calibration')
            self.cal_result = True
            return [None, None, event_value, self.PowerWashI, self.CSE, self.cal_result]
