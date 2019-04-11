from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
import pickle
import seaborn as sns
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler
from pandas.plotting import scatter_matrix
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import serial
import os
import sys


class DataHandler:
    WINDOW = 10
    COLUMNS = ['sv', 'sc', 'srp', 'sap',
               'bv', 'bc', 'brp', 'bap']
    MEAN_COLUMNS = ['sv-ma', 'sc-ma', 'srp-ma', 'sap-ma',
                    'bv-ma', 'bc-ma', 'brp-ma', 'bap-ma']
    STD_COLUMNS = ['sv-std', 'sc-std', 'srp-std', 'sap-std',
                   'bv-std', 'bc-std', 'brp-std', 'bap-std']

    def __init__(self):
        self.features = None
        self.target = None
        self.df = None

    def read_dataset(self):
        df = pd.read_csv('full_dataset.csv')

        rolling_mean = df.iloc[:, :8].rolling(window=self.WINDOW).mean()
        rolling_mean.columns = self.MEAN_COLUMNS

        rolling_std = df.iloc[:, :8].rolling(window=self.WINDOW).std()
        rolling_std.columns = self.STD_COLUMNS

        df = pd.concat([rolling_mean, rolling_std, df], axis=1)
        df = df[np.isfinite(df['sv-ma'])]
        self.df = df.sample(frac=1).reset_index(drop=True)

        self.features = self.df.columns[:24]
        self.target = self.df.columns[24:]

    def normalize_data(self):
        scaler = MinMaxScaler(feature_range=(0, 1))
        rescaled = scaler.fit_transform(self.df[self.features])
        rescaled = pd.DataFrame(rescaled,
                                columns=self.MEAN_COLUMNS + self.STD_COLUMNS + self.COLUMNS)
        self.df = pd.concat([rescaled, self.df[self.target]], axis=1)

    def calc_accuracy(self, test, predictions):
        acc = accuracy_score(test[self.target], predictions)
        return acc

    def calc_cm(self, test, predictions):
        return confusion_matrix(test[self.target].iloc[:, [0]], predictions)

    def calc_roc(self, test, predictions):
        roc_auc = roc_auc_score(test[self.target], predictions)
        return roc_auc

    def calc_classification_report(self, test, predictions):
        report = classification_report(test[self.target], predictions)
        report_dict = classification_report(test[self.target], predictions, output_dict=True)
        return report, report_dict

    def plot_roc(self, test, predictions):
        fpr, tpr, threshold = roc_curve(test[self.target], predictions)
        roc_auc = self.calc_roc(test, predictions)

        plt.title('Receiver Operating Characteristic')
        plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
        plt.legend(loc='lower right')
        plt.plot([0, 1], [0, 1], 'r--')
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.show()

        return roc_auc

    def plot_scatter(self):
        color_map = cm.get_cmap('gnuplot')
        scatter_matrix(self.df.iloc[:, 16:24],
                       c=self.df[self.target].values.ravel(),
                       marker='o',
                       s=30,
                       hist_kwds={'bins': 15},
                       cmap=color_map)

        plt.show()

    def plot_comparative(self, test, predictions):
        comparative = test[self.target].copy()
        comparative.loc[:, 'fault_prediction'] = predictions

        # comparative.plot(style=['o', 'rx'])
        comparative.plot()
        plt.show()


class DataReader:
    def __init__(self, port):
        self.serial_port = serial.Serial(port=port,
                                         baudrate=9600,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS)

    def read_sample(self):
        split_str = []
        while len(split_str) != 8:
            message_bytes = self.serial_port.readline()
            try:
                split_str = message_bytes.decode("utf-8").split(',')
            except UnicodeDecodeError as e:
                print(e)

        read_values = [float(split_str[0]), float(split_str[1]), float(split_str[2]), float(split_str[3]),
                       float(split_str[4]), float(split_str[5]), float(split_str[6]), float(split_str[7])]
        return read_values


class RandomForest:

    def __init__(self):
        self.clf = None
        # Gets the file path to the fbt (xml) file
        self.filename = os.path.join(os.path.dirname(sys.path[0]),
                                     'resources',
                                     'function_blocks',
                                     'arm_config',
                                     'rf_model.pickle')
        self.data = DataHandler()
        # self.data.read_dataset()

    def save_model(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.clf, f)

    def load_model(self):
        with open(self.filename, 'rb') as f:
            self.clf = pickle.load(f)

    def build_model(self, estimators):
        self.clf = RandomForestClassifier(n_estimators=estimators)

    def train_model(self):
        self.clf.fit(self.data.df[self.data.features],
                     self.data.df[self.data.target].values.ravel())

    def feature_extraction(self):
        rfe = RFE(self.clf, 3)
        fit = rfe.fit(self.data.df[self.data.features],
                      self.data.df[self.data.target].values.ravel())
        print("Num Features: {0}".format(fit.n_features_))
        print("Selected Features: {0}".format(fit.support_))
        print("Feature Ranking: {0}".format(fit.ranking_))

    def cross_validation(self):
        estimators = [50, 100, 250, 500]
        auc_max = 0
        best_estimator = 0
        kf = KFold(n_splits=4, shuffle=True)
        for train_index, test_index in kf.split(self.data.df.values):
            x_train = self.data.df[self.data.features].iloc[train_index, :]
            x_test = self.data.df[self.data.features].iloc[test_index, :]
            y_train = self.data.df[self.data.target].iloc[train_index, :]
            y_test = self.data.df[self.data.target].iloc[test_index, :]

            estimator = estimators.pop()
            model = RandomForestClassifier(n_estimators=estimator)

            model.fit(x_train, y_train.values.ravel())

            predictions = model.predict(x_test)

            auc = self.data.calc_roc(y_test, predictions)
            accuracy = self.data.calc_accuracy(y_test, predictions)
            report, report_dict = self.data.calc_classification_report(y_test, predictions)

            if auc > auc_max:
                auc_max = auc
                best_estimator = estimator

            print('\n\nmodel: {0}\nroc_auc: {1}\naccuracy: {2}\n'.format(estimator, auc, accuracy))
            print(report)

        return best_estimator

    def grid_search(self):
        model = RandomForestClassifier(n_jobs=-1, random_state=42, verbose=2)

        grid = {'n_estimators': [10, 13, 18, 25, 33, 45, 60, 81, 110, 148, 200],
                'max_features': [0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21, 0.23, 0.25],
                'min_samples_split': [2, 3, 5, 8, 13, 20, 32, 50, 80, 126, 200]}

        rf_grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=4,
                                      verbose=2, return_train_score=True)

        rf_grid_search.fit(self.data.df[self.data.features], self.data.df[self.data.target].values.ravel())

        df_grid_search = pd.DataFrame(rf_grid_search.cv_results_)

        max_scores = df_grid_search.groupby(['param_min_samples_split',
                                             'param_max_features']).max()
        max_scores = max_scores.unstack()[['mean_test_score', 'mean_train_score']]
        sns.heatmap(max_scores.mean_test_score, annot=True, fmt='.4g')
        plt.show()


class COLLAB_FOREST:

    def __init__(self):
        self.reader = None
        self.values_df = None
        self.rf = None

    def schedule(self, event_name, event_value, sv, sc, srp, sap, bv, bc, brp, bap):

        if event_name == 'INIT':
            # Gets the file path to the fbt (xml) file
            csv_path = os.path.join(os.path.dirname(sys.path[0]),
                                    'resources',
                                    'function_blocks',
                                    'arm_config',
                                    'input_data.csv')
            self.values_df = pd.read_csv(csv_path)
            self.rf = RandomForest()
            self.rf.load_model()
            return [event_value, None, None]

        elif event_name == 'PREDICT':
            self.values_df.loc[len(self.values_df)] = [sv, sc, srp, sap, bv, bc, brp, bap]

            rolling_mean = self.values_df.rolling(window=self.rf.data.WINDOW).mean()
            rolling_mean.columns = self.rf.data.MEAN_COLUMNS

            rolling_std = self.values_df.rolling(window=self.rf.data.WINDOW).std()
            rolling_std.columns = self.rf.data.STD_COLUMNS

            mix_df = pd.concat([rolling_mean, rolling_std, self.values_df], axis=1)

            prevision = self.rf.clf.predict(mix_df.iloc[[-1]])
            if prevision == 0:
                return [None, event_value, None]
            elif prevision == 1:
                return [None, event_value, event_value]
