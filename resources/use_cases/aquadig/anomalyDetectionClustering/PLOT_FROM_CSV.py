import numpy as np
import re
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import string


class PLOT_FROM_CSV:

    def __init__(self):
        self.csv_path=""
        self.name=""
        self.plt_path=""


    def schedule(self, event_input_name, event_input_value, csv_path, csv_name, plot_path, plot_name):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            path = os.path.join(*re.split('\\/', csv_path), csv_name)
            data = pd.read_csv(path)
            labels = np.random.choice(list(string.ascii_lowercase), size=data.shape[1] - 1, replace=False)
            labels = np.hstack((labels, "label"))
            data = pd.read_csv(path, names=labels)

            axis = data.loc[data["label"] == False].plot(x=labels[0], y=labels[1], kind="scatter", color="g",
                                                         label='Normal')
            data.loc[data["label"] == True].plot(x=labels[0], y=labels[1], kind="scatter", color="r", ax=axis, label="Anomaly")
            axis.legend()
            plt.title("Normal Behaviour vs. Anomaly")

            self.plt_path = os.path.join(*re.split('\\/', plot_path), plot_name)
            plt.savefig(str(self.plt_path)+'.png', dpi="figure")
            plt.show()

            return [None, event_input_value, "ok"]