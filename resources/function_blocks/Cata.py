

class Cata:

    def __init__(self):
        self.temperature = 0
        self.pressure = 0
        self.process_time = 0

    def schedule(self, event_name, event_value):
        if event_name == 'Init':
            return [event_value, event_value, None, self.temperature, self.pressure, self.process_time, False]

        elif event_name == 'Read':
            self.temperature += 1
            self.pressure += 2
            self.process_time += 3
            return [None, event_value, None, self.temperature, self.pressure, self.process_time, False]

        elif event_name == 'Calibrate':
            return [None, None, event_value, self.temperature, self.pressure, self.process_time, True]
