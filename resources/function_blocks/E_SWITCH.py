import time


class E_SWITCH:

    def __init__(self):
        self.EO0 = 0
        self.EO1 = 0

    def schedule(self, event_name, event_value, G):
        if event_name == 'EI':
            self.EO0 = event_value + 1
            time.sleep(1)
            return [self.EO0, None]

