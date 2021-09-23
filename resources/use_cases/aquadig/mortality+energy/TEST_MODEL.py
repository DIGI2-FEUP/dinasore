import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

class TEST_MODEL:

    def __init__(self):
        self.x=[]
        self.title_to_df=""


    def schedule(self, event_input_name, event_input_value, X, model, n_points, lw, up):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            lw=np.array(eval(lw))
            up=np.array(eval(up))
            self.title_to_df = ['x0']
            for i in range(np.array(X).shape[1] - 2):
                self.title_to_df = self.title_to_df + ['x{0:d}'.format(i + 1)]
            self.title_to_df = self.title_to_df + ['f(x)']

            test_points_df = np.hstack((np.hstack(
                (np.random.uniform(lw[0], up[0], (n_points, 1)), np.random.uniform(lw[1], up[1], (n_points, 1)))),
                                        np.random.uniform(lw[2], up[2], (n_points, 1))))
            predictions = model.predict(test_points_df).reshape(-1, 1)
            test_points_df = pd.DataFrame(np.hstack((test_points_df, predictions)), columns=self.title_to_df)
            return [None, event_input_value, test_points_df]