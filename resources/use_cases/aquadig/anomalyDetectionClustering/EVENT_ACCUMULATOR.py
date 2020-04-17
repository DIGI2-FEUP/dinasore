import numpy as np

class EVENT_ACCUMULATOR:

    def __init__(self):
        self.measurements_list=[]
        self.window_width=0
        self.output=[]

    def schedule(self, event_name, event_value, measurement, window_width):

        if event_name == 'INIT':

            return [event_value, None, None, [], 0]

        elif event_name == 'RUN':

            if window_width is None:
                self.window_width = 20
            else:
                self.window_width = window_width

            if len(self.measurements_list) == 0:
                self.measurements_list = np.copy([measurement])
            elif len(self.measurements_list) == self.window_width - 1:
                self.measurements_list = np.append(self.measurements_list, measurement)
                self.output = np.copy(self.measurements_list)
                self.measurements_list = np.copy(self.output[int(self.window_width/4):])
                return [None, event_value, event_value, self.output, self.window_width]

            else:
                self.measurements_list = np.append(self.measurements_list, measurement)

            return [None, event_value, None, [], self.window_width]

        elif event_name == 'VECTOR_READY':
            return [None, None, event_value,  [], self.window_width]
