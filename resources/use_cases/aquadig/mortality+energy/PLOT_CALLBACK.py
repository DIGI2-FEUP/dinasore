import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

class PLOT_CALLBACK:

    def __init__(self):
        self.x=[]


    def schedule(self, event_input_name, event_input_value, Test_points, callbak, title):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            if (type(Test_points.columns) == pd.core.indexes.range.RangeIndex):
                df=pd.DataFrame(Test_points)
                img = ax.scatter(df[0], df[1], df[2], c=df[3], cmap=plt.hot())
            else:
                img = ax.scatter(Test_points['x0'], Test_points['x1'], Test_points['x2'], c=Test_points['f(x)'], cmap=plt.hot())
            fig.colorbar(img)
            ax.set_xlabel('x0', color='gray')
            ax.set_ylabel('x1', color='gray')
            ax.set_zlabel('x2', color='gray')
            if title is not None:
                ax.set_title(title)

            opt_test = pd.DataFrame(callbak)
            ax.plot(np.array(opt_test['x0']), np.array(opt_test['x1']), np.array(opt_test['x2']), color='green', marker='o')
            last_sample = np.array(opt_test.iloc[len(opt_test) - 1])
            ax.scatter(last_sample[0], last_sample[1], last_sample[2], color='blue', marker='*')
            plt.show()

            return [None, event_input_value,"ok"]