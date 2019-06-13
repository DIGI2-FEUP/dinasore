import time

class SLEEP:

    def schedule(self, event_name, event_value):
        if event_name == 'SLEEP':
            time.sleep(1)
            return [event_value]

