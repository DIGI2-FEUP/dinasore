

class TEST_SERVICE:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, rate, signal):
        if event_name == 'INIT':
            return [event_value, None, None, rate + 1, False]

        elif event_name == 'RUN':
            return [None, event_value, None, signal + rate, True]

        elif event_name == 'CALIBRATE':
            return [None, None, event_value, signal + rate + 1, True]
