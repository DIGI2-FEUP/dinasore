import numpy as np
import time


class MACHINE_SIMULATOR:

    def __init__(self):
        self.state = 'IDLE'
        self.prev_state = 'WORK'
        self.ttf = 0
        self.tts = 0
        self.ttr = 0
        self.mtta = 0

    def schedule(self, event_name, event_value, params_data, lim_anom, params_mtbf, params_mtts, params_mttr, delay):
        if event_name == 'INIT':
            # init the states
            self.state = 'IDLE'
            self.prev_state = 'WORK'
            # computes (gets from the distribution) the ttf
            self.ttf = self.generate_time(params_mtbf)
            self.mtta = self.ttf*lim_anom
            return [event_value, None, '', self.state]

        elif event_name == 'READ':
            # checks the state
            if self.state == 'IDLE':
                time.sleep(delay)
                return [None, None, '', self.state]

            elif self.state == 'WORK':
                # wait some time (performs the work)
                time.sleep(delay)
                # computes (decreases) the current TTF
                self.ttf -= delay
                # checks if is 0 -> failure
                if self.ttf <= 0:
                    # computes (gets from the distribution) the tts (time to start the repair)
                    self.tts = self.generate_time(params_mtts)
                    self.state = 'BREAK'
                    return [None, event_value, '', self.state]
                # normal operation
                else:
                    # generates data
                    anom = 1 if self.ttf <= self.mtta else 0
                    data_str = self.generate_data(params_data, anom)
                    return [None, event_value, data_str, self.state]

            elif self.state == 'BREAK':
                # simulates the waiting time to repair
                time.sleep(delay)
                # computes (decreases) the current TTF
                self.tts -= delay
                # checks if is 0 -> starts repairing
                if self.tts <= 0:
                    # computes (gets from the distribution) the ttr (time to repair)
                    self.ttr = self.generate_time(params_mttr)
                    self.state = 'REPAIR'
                    return [None, event_value, '', self.state]
                # break state
                else:
                    return [None, event_value, '', self.state]

            elif self.state == 'REPAIR':
                # simulates the waiting time to repair
                time.sleep(delay)
                # computes (decreases) the current TTF
                self.ttr -= delay
                # checks if is 0 -> starts repairing
                if self.ttr <= 0:
                    # computes (gets from the distribution) the ttr (time to repair)
                    self.ttf = self.generate_time(params_mtbf)
                    self.mtta = self.ttf * lim_anom
                    self.state = 'WORK'
                    return [None, event_value, '', self.state]
                # break state
                else:
                    return [None, event_value, '', self.state]

        elif event_name == 'ON-OFF':
            # switches the button
            if self.state == 'IDLE':
                # updates the data
                self.state = self.prev_state
                return [None, event_value, '', self.state]
            else:
                self.prev_state = self.state
                self.state = 'IDLE'
                return [None, None, '', self.state]

    @staticmethod
    def generate_data(params_str, anom):
        params = list(eval(params_str))
        # generates the values
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
        return data_str

    @staticmethod
    def generate_time(params_str):
        params = list(eval(params_str))
        t = round(np.random.normal(params[0], params[1]))
        return t
