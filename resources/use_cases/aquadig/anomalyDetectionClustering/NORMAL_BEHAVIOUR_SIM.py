import numpy as np

class NORMAL_BEHAVIOUR_SIM:

    def __init__(self):
        self.column_out=[]
        self.size=[]



    def schedule(self, event_input_name, event_input_value, MEAN, STD, SIZE):

        if event_input_name == 'INIT':
            return [event_input_value, None, self.column_out, self.size]

        elif event_input_name == 'RUN':
            # generates the gaussian distribution
            self.column_out = np.random.normal(MEAN, STD, SIZE)
            #reshapes the data to look like a column
            self.column_out = np.reshape(self.column_out, (len(self.column_out), 1))

            self.size=self.column_out.shape
            return [None, event_input_value, self.column_out, self.size]
