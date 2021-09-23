import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from sklearn.pipeline import Pipeline


class RIDGE_MODEL:

    def __init__(self):
        self.csv_path=""
        self.name=""
        self.plt_path=""


    def schedule(self, event_input_name, event_input_value, X, Y, degree, alpha):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            pipe = Pipeline(
                [('poly', PolynomialFeatures(degree=degree)), ('scaler', MinMaxScaler(feature_range=(0,1))),
                 ('clf', linear_model.Ridge(alpha=alpha))])
            pipe.fit(X, Y)
            return [None, event_input_value, pipe]