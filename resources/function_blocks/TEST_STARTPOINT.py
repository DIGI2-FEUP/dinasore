

class TEST_STARTPOINT:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value):
        if event_name == 'INIT':
            return [event_value, None, None, 23, False]

        elif event_name == 'READ':
            return [None, event_value, None, 32, True]

        elif event_name == 'CALIBRATE':
            return [None, None, event_value, 32, True]
