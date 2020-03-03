import threading
import random
import time


class TIMER_SIMULATION:

    def __init__(self):
        self.upper_limit = 0

    def schedule(self, event_name, event_value, ua_name, event_identifier, ideal, range_prob, range_str):

        # initial check
        if (ua_name is None) or (event_identifier is None) or (ideal is None):
            return [None, None, None, None]

        if event_name == 'INIT':
            # print("INIT limit=", self.upper_limit)
            return [event_value, None, None, round(self.upper_limit, 2)]

        if event_name == 'RUN':
            # print("RUN limit=", self.upper_limit)
            return [None, None, None, round(self.upper_limit, 2)]

        elif event_name == 'TRIGGER':
            # print("TRIGGER event_name=", event_name)
            if event_value == event_identifier:
                # print("TRIGGER event_value == event_identifier=", event_name)
                if (int(range_prob) != 0) and (random.randint(0, 100) < int(range_prob)):
                    # print("!!!!!!!!!!!!!!!  if range_prob=", int(range_prob))
                    value_button, value_top = range_str.split('-')
                    # get the random value between the range
                    self.upper_limit = random.random() * (int(value_top) - int(value_button)) + int(value_button)
                else:
                    # print("!!!!!!!!!!!!!!!ideal=", int(ideal))
                    # get the ideal value
                    self.upper_limit = int(ideal)

                # print("TRIGGER limit=", round(self.upper_limit, 2))
                time.sleep(round(self.upper_limit, 2))
                return [None, None, event_identifier,
                        round(self.upper_limit, 2)]

            # print("TRIGGER2222 limit=", round(self.upper_limit, 2))
            return [None, None, None,
                    round(self.upper_limit, 2)]
