

class PROCESS_TIME:

    def __init__(self):
        self.process_time = 0

    def schedule(self, event_name, event_value):
        if event_name == 'INIT':
            return [event_value, event_value, None, self.process_time, False]

        elif event_name == 'READ':
            self.process_time += 1
            return [None, event_value, None, self.process_time, False]

        elif event_name == 'CALIBRATE':
            return [None, None, event_value, self.process_time, True]
