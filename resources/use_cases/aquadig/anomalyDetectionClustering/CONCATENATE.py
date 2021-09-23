import numpy as np

class CONCATENATE:

    def __init__(self):
        self.data1=None
        self.data2=None
        self.result=None


    def schedule(self, event_input_name, event_input_value,data1, data2):

        if event_input_name == 'INIT':
            return [event_input_value, None, self.result]

        elif event_input_name == 'RUN':
            self.data1=np.array(data1)
            self.data2=np.array(data2)
            self.result=np.vstack((data1, data2))
            return [None, event_input_value, self.result]