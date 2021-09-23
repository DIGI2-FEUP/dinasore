import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt

class PLOT_4D:

    def __init__(self):
        self.x=[]


    def schedule(self, event_input_name, event_input_value, X, title):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            df = pd.DataFrame(X)
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            #if model is not None:
            #    img = ax.scatter(df[0], df[1], df[2], c=model.predict(df.iloc[:,0:3]), cmap=plt.hot())
            #else:
            if (type(df.columns) == pd.core.indexes.range.RangeIndex):
                img = ax.scatter(df[0], df[1], df[2], c=df[3], cmap=plt.hot())
            else:
                img = ax.scatter(X['x0'], X['x1'], X['x2'], c=X['f(x)'], cmap=plt.hot())
            ax.set_xlabel('x0', color='gray')
            ax.set_ylabel('x1', color='gray')
            ax.set_zlabel('x2', color='gray')
            if title is not None:
                ax.set_title(title)
            fig.colorbar(img)
            plt.show()

            return [None, event_input_value,"ok"]