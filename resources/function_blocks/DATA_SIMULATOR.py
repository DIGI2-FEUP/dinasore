from scipy.stats import bernoulli
import numpy as np
import time


class DATA_SIMULATOR:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, params_str, ratio, delay):
        if event_name == 'INIT':
            # doesn't need initialization
            return [event_value, None, '']

        elif event_name == 'READ':
            params = list(eval(params_str))
            # generates the values
            anom = bernoulli.rvs(ratio)
            sample = []
            for norm_param, anom_param in params:
                # checks if an anomaly to generate
                mu, std = norm_param if anom == 0 else anom_param
                # generates the value
                value = round(np.random.normal(mu, std), 3)
                # stores the value
                sample.append(value)
            # appends the anom at the end and converts it to string
            sample.append(anom)
            data_str = ','.join(['{0}'.format(x) for x in sample])
            # wait some time
            time.sleep(delay)
            return [None, event_value, data_str]
