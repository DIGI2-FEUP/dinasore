import time
import string
import random


class CHASSIS_GENERATOR:

    def __init__(self):
        self.transporter_index = 0
        self.proceed = False
        self.waited = False
        self.first = True

    def schedule(self, event_name, event_value, n_chassis, sample_rate):
        if event_name == 'INIT':
            return [event_value, None, None,
                    None, None]

        elif event_name == 'SYNC':
            self.proceed = True
            return [None, None, None,
                    None, None]

        elif event_name == 'READ':
            if (not self.waited):
                self.transporter_index += 1
                # reset the index
                if self.transporter_index >= int(n_chassis):
                    self.transporter_index = 0
                # wait some time
                time.sleep(int(sample_rate))

                self.waited = True
                return [None, event_value, None,
                        None, None]
            else:
                if (self.first):
                    self.proceed = False
                    self.waited = False
                    self.first = False
                    # send chassis and transporter
                    # set the output values
                    transporter = 'T{0}'.format(self.transporter_index)
                    keys = string.ascii_uppercase + string.digits
                    chassis = ''.join([random.choice(keys) for _ in range(5)])

                    return [None, event_value, self.transporter_index,
                            chassis, transporter]
                # can send chassis
                if (self.proceed):
                    self.proceed = False
                    self.waited = False

                    # set the output values
                    transporter = 'T{0}'.format(self.transporter_index)
                    keys = string.ascii_uppercase + string.digits
                    chassis = ''.join([random.choice(keys) for _ in range(5)])


                    # send chassis and transporter
                    return [None, event_value, self.transporter_index,
                            chassis, transporter]
                else:
                    time.sleep(0.5)
                    # waits for next iteration
                    return [None, event_value, None,
                            None, None]
