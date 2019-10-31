import numpy as np
import time


def create_distribution(offset, upper_limit):
    x = np.linspace(0, 2 * np.pi, 201)
    # create the sin function
    sin_x = (np.sin(x) + 1) * ((upper_limit - offset) / 2) + offset
    # add the noise
    noise = np.random.normal(0, (upper_limit - offset) * 0.05, 201)
    sin_x = sin_x + noise
    # split the array to start in a random place
    split_value = np.random.randint(0, 201)
    sin_x = abs(np.concatenate([sin_x[split_value:], sin_x[0:split_value]]))
    return sin_x


class SENSOR_SIMULATOR_RANGE:

    def __init__(self):
        self.distribution = None
        self.sample_rate = 1
        self.distribution_index = 0
        self.actual_value = 0
        self.actual_list = []
        self.values_list = []
        self.actual_state = 'stop'

    def schedule(self, event_name, event_value, ua_name, event_identifier, range_str, is_batch, rate):

        if event_name == 'INIT':
            values_range = range_str.split('-')
            self.sample_rate = 1 / float(rate)
            # create the values list (distribution) and reset the index
            self.distribution = create_distribution(float(values_range[0]), float(values_range[1]))
            self.distribution_index = 0
            return [event_value, None, None, '0']

        elif event_name == 'READ':
            if self.actual_state == 'work':
                self.actual_value = self.distribution[self.distribution_index]
                self.distribution_index += 1
                # appends the value to the list
                self.values_list.append(str(self.actual_value))
                # reset the index
                if self.distribution_index >= len(self.distribution):
                    self.distribution_index = 0
            else:
                self.actual_value = 0

            # wait some time
            time.sleep(self.sample_rate)

            # checks if is batch or continuous
            if int(is_batch) == 0:
                return [None, event_value, None, str(self.actual_value)]
            else:
                return [None, event_value, None, ','.join(self.actual_list)]

        elif event_name == 'TRIGGER':
            if self.actual_state == 'stop':
                # starts the work
                self.actual_state = 'work'
                # resets the list
                self.values_list = []

            elif self.actual_state == 'work' and event_value == event_identifier:
                # starts the work
                self.actual_state = 'stop'
                # passes the values_list to the actual_list
                self.actual_list = self.values_list.copy()

            # checks if is batch or continuous
            if int(is_batch) == 0:
                return [None, event_value, None, str(self.actual_value)]
            else:
                return [None, event_value, None, ','.join(self.actual_list)]
