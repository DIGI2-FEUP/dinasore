import numpy as np
class LABELLING:

    def __init__(self):
        self.data_in=[]
        self.label=[]
        self.data_out=[]
        self.status=[]
        


    def schedule(self, event_input_name, event_input_value, Data, Label):

        if event_input_name == 'INIT':
            return [event_input_value, None, self.data_out, self.status]

        elif event_input_name == 'RUN':
            self.data_in = np.array(Data)
            if np.array(Data).ndim == 1:
                self.data_out = np.array(str(Label))
                self.data_out = np.hstack((self.data_in, self.data_out))
                self.status = "ok"
                return [None, event_input_value, self.data_out, self.status]
            else:
                self.data_out = (np.array([str(Label)] * (self.data_in.shape[0]))).reshape((self.data_in.shape[0], 1))

                self.data_out = np.hstack((self.data_in, self.data_out))
                self.status = "ok"
                if (self.data_out.shape[0] == self.data_in.shape[0]) and self.data_out.size > 0:
                    return [None, event_input_value, self.data_out, self.status]
                else:
                    return [None, event_input_value, [], "not ok"]