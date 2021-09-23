import numpy as np

import matplotlib.pyplot as plt
import re
import os

class PLOT_2_CURVES:

    def __init__(self):
        self.x=[]


    def schedule(self, event_input_name, event_input_value, df_to_plot, curve1_name, curve2_name, title, plot_path, plot_name):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':

            fig, ax1 = plt.subplots()

            color = 'tab:red'
            ax1.set_xlabel('alpha')
            ax1.set_ylabel(curve1_name, color=color)
            ax1.plot(df_to_plot["alpha"], df_to_plot[curve1_name], color=color, marker='.')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_title('Optimization for different alpha values')
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

            color = 'tab:blue'
            ax2.set_ylabel(curve2_name, color=color)  # we already handled the x-label with ax1
            ax2.plot(df_to_plot["alpha"], df_to_plot[curve2_name], color=color, marker='.')
            ax2.tick_params(axis='y', labelcolor=color)

            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            plt.title(title)

            self.plt_path = os.path.join(*re.split('\\/', plot_path), plot_name)
            plt.savefig(str(self.plt_path) + '.png', dpi="figure")

            plt.show()


            return [None, event_input_value, "ok"]