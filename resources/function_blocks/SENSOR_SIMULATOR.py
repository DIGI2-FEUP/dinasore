import numpy as np
import time


def create_distribution(offset):
    # generate values based in the normal distribution
    mu, sigma = 0.5, 0.1
    s = np.random.normal(mu, sigma, 3000)
    # organizes the values in a normal curve
    hist, bin_edges = np.histogram(s, bins=np.arange(0.2, 0.8, 0.002))
    values2sort = offset + (hist / 4)
    # split the array to start in a random place
    split_value = np.random.randint(0, 300)
    final_values = np.concatenate([values2sort[split_value:], values2sort[0:split_value]])
    return final_values


class SENSOR_SIMULATOR:

    def __init__(self):
        self.distribution = None
        self.distribution_index = 0

    def schedule(self, event_name, event_value, offset):
        if event_name == 'INIT':
            # create the values list (distribution) and reset the index
            self.distribution = create_distribution(offset)
            self.distribution_index = 0
            return [event_value, None, 0]

        elif event_name == 'READ':
            value = self.distribution[self.distribution_index]
            self.distribution_index += 1
            # reset the index
            if self.distribution_index >= len(self.distribution):
                self.distribution_index = 0
            # wait some time
            time.sleep(1)
            return [None, event_value, value]
