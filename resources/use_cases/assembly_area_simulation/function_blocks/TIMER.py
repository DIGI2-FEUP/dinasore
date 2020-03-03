import threading
import random
import time


class TIMER:

    def __init__(self):
        self.upper_limit = 0

    def schedule(self, event_name, event_value, ua_name, event_identifier, range_str):

        # initial check
        if (ua_name == None) or (event_identifier == None) or (range_str == None):
            return [None, None, None,
                    None]

        if event_name == 'INIT':
            return [event_value, None, None,
                    round(self.upper_limit,2)]

        if event_name == 'RUN':
            return [None, None, None,
                    round(self.upper_limit,2)]

        elif event_name == 'TRIGGER':
            if event_value == event_identifier:
                value_button, value_top = range_str.split('-')
                # get the random value between the range
                self.upper_limit = random.random() * (int(value_top) - int(value_button)) + int(value_button)
                time.sleep(round(self.upper_limit,2))

                return [None, None, event_identifier,
                        round(self.upper_limit,2)]

            return [None, None, None,
                    round(self.upper_limit,2)]
