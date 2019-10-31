import time
import string
import random


class CHASSIS_GENERATOR:

    def __init__(self):
        self.transporter_index = 0

    def schedule(self, event_name, event_value, n_chassis, sample_rate):
        if event_name == 'INIT':
            transporter = 'T{0}'.format(self.transporter_index)
            keys = string.ascii_uppercase + string.digits
            chassis = ''.join([random.choice(keys) for _ in range(5)])
            return [event_value, None, event_value, chassis, transporter]

        elif event_name == 'READ':
            self.transporter_index += 1
            # reset the index
            if self.transporter_index >= int(n_chassis):
                self.transporter_index = 0
            # wait some time
            time.sleep(int(sample_rate))
            # set the output values
            transporter = 'T{0}'.format(self.transporter_index)
            keys = string.ascii_uppercase + string.digits
            chassis = ''.join([random.choice(keys) for _ in range(5)])
            return [None, event_value, event_value, chassis, transporter]
