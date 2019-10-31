import random
import time


class TIMER:

    def __init__(self):
        self.counter = 0
        self.upper_limit = 0
        self.actual_state = 'stop'

    def schedule(self, event_name, event_value, ua_name, event_identifier, range_str):
        if event_name == 'INIT':
            return [event_value, None, None, self.counter, 0]

        elif event_name == 'READ':

            if self.actual_state == 'work':
                self.counter += 1
                # reset the index
                if self.counter >= self.upper_limit:
                    # sets the value output to the upper limit
                    self.counter = self.upper_limit
                    self.actual_state = 'stop'
                    # wait some time
                    time.sleep(1)
                    return [None, '1', event_identifier, self.counter, 0]

            # wait some time
            time.sleep(1)
            return [None, '1', None, self.counter, 0]

        elif event_name == 'TRIGGER':
            if self.actual_state == 'stop' and event_value == event_identifier:
                # resets the counter
                self.counter = 0
                self.actual_state = 'work'
                # simulates a new value
                value_button, value_top = range_str.split('-')
                # get the random value between the range
                self.upper_limit = random.random() * (int(value_top) - int(value_button)) + int(value_button)
            return [None, '1', None, self.counter, 0]
