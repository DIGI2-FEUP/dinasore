import numpy as np
import pickle
import os
import pandas as pd
import re

class LOADING_PICKLE:

    def __init__(self):
        self.path=""
        self.data=[]
        self.status=[]

    def schedule(self, event_input_name, event_input_value, path, name):

        if event_input_name == 'INIT':
            return [event_input_value, None, self.data, self.status]

        elif event_input_name == 'RUN':
            if path is None:
                self.status = "Error in specifying path"
                return [None, event_input_value, self.data, self.status]

            self.path = os.path.join(*re.split('\\/', path), name)

            try:
                with open(self.path, 'rb') as f:
                    self.data = pickle.load(f)

                self.status = 'Ok'
                return [None, event_input_value, self.data, self.status]
            except OSError:
                return [None, event_input_value, self.data, "Not_ok"]
