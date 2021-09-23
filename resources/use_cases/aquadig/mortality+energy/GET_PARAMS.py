import numpy as np
import re
import os
import pandas as pd



class GET_PARAMS:

    def __init__(self):
        self.csv_path=""
        self.name=""
        self.plt_path=""


    def schedule(self, event_input_name, event_input_value, csv_path, csv_name):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            path = os.path.join(*re.split('\\/', csv_path), csv_name)

            data = np.array(pd.read_csv(path, header=None).values)

            return [None, event_input_value, data]