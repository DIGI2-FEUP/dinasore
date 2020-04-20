import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

class TRAIN_TEST_SPLIT_FB:

    def __init__(self):
        self.X=[]
        self.y=[]
        self.prop=0


    def schedule(self, event_input_name, event_input_value, X_y_in, prop):
        if event_input_name == 'INIT':
            return [event_input_value, None, None, None, None, None]

        elif event_input_name == 'RUN':

            self.X = np.array(X_y_in[:, 0: X_y_in.shape[1] - 1])
            self.y = np.array(X_y_in[:, -1])

            if prop is None:
                self.prop = 0.2
            else:
                if prop==0:
                    return [None, event_input_value, self.X, None, self.y, None]
                else:

                    self.prop = float(prop)

                    X_train, X_test, y_train, y_test = \
                        train_test_split(self.X, self.y, test_size=self.prop, random_state=42)

                    return [ None, event_input_value, X_train, X_test, y_train, y_test]