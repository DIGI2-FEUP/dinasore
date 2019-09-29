

class TEST_ENDPOINT:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, rate, signal):
        if event_name == 'INIT':
            # print('initialization')
            return [event_value, None, None, False]

        elif event_name == 'RUN':
            return [None, event_value, None, True]

        elif event_name == 'CALIBRATE':
            return [None, None, event_value, True]
