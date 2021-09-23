import pickle
import re
import os

class SAVING_PICKLE:

    def __init__(self):
        self.path=""
        self.data=""
        self.status=""


    def schedule(self, event_input_name, event_input_value, data_in, path, name):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':

            if path is None or name is None:
                self.status = "Error in specifying path/name"
                return [None, event_input_value, self.status]
            else:
                self.data = data_in
                self.path=os.path.join(*re.split('\\/', path), name)

            try:
                with open(self.path, 'wb') as f:
                    pickle.dump(self.data, f)
                return [None, event_input_value, "OK"]
            except OSError:
                return [None, event_input_value, "NOT_OK"]