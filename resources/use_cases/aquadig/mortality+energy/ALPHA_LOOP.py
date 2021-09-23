import numpy as np
import pandas as pd

class ALPHA_LOOP:

    def __init__(self):
        self.alpha=0
        self.alpha_step=0
        self.df_to_plot=[]

    def schedule(self, event_name, event_value, alpha_step, res, model1, model2):

        if event_name == 'INIT':

            return [event_value, None, None, None, 0, []]

        elif event_name == 'RUN':
            model1_res = model1.predict(res.x.reshape(1, -1))
            model2_res = model2.predict(res.x.reshape(1, -1))
            if len(self.df_to_plot) == 0:
                self.df_to_plot = np.hstack((np.hstack((np.hstack((np.array(res.x), self.alpha)), model1_res)), model2_res))

            else:
                self.df_to_plot = np.vstack((self.df_to_plot, np.hstack(
                    (np.hstack((np.hstack((np.array(res.x), self.alpha)), model1_res)), model2_res))))

            self.alpha=self.alpha+self.alpha_step
            if self.alpha >1:
                self.df_to_plot = pd.DataFrame(self.df_to_plot, columns=["x", "y", "z", "alpha", "mort", "energy"])
                return [None, None, None, event_value, self.alpha, self.df_to_plot]

            return [None, event_value, None, None, self.alpha, []]

        elif event_name == 'START':
            self.df_to_plot = []
            self.alpha_step = alpha_step

            return [None, event_value, event_value, None, self.alpha, []]

        elif event_name == 'DONE':

            return [ event_value, None, None, None, self.alpha, []]


