from sklearn.svm import OneClassSVM
import numpy as np

class ONE_CLASS_SVM:

    def __init__(self):
        self.classifier=None
        self.prediction=None
        self.score=None
        self.predict_proba=None

        self.kernel='rbf'
        self.degree=3
        self.gamma='scale'
        self.coef0=0.0
        self.tol=0.001
        self.nu=0.5
        self.shrinking=True
        self.cache_size=200
        self.verbose=False
        self.max_iter=-1


    def schedule(self, event_input_name, event_input_value, data_from_pickle, X_predict, X_train, y_train,
                 kernel, degree, gamma, coef0, tol, nu, shrinking, cache_size, verbose, max_iter):

        if event_input_name == 'INIT':

            return [event_input_value, None, self.classifier, self.prediction, self.score]

        elif event_input_name == 'RUN':
            if data_from_pickle == None:
                # default values or not
                if kernel is not None:
                    self.kernel = kernel
                if degree is not None:
                    self.degree = degree
                if gamma is not None:
                    if gamma =='scale' or gamma=='auto':
                        self.gamma = gamma
                    else:
                        self.gamma=float(gamma)
                if coef0 is not None:
                    self.coef0 = coef0
                if tol is not None:
                    self.tol = tol
                if nu is not None:
                    self.nu = nu
                if shrinking is not None:
                    self.shrinking = shrinking
                if cache_size is not None:
                    self.cache_size = cache_size
                if verbose is not None:
                    self.verbose = verbose
                if max_iter is not None:
                    self.max_iter = max_iter

                classif = OneClassSVM( )

                classif.fit(np.array(X_train).astype(np.float64), np.array(y_train).astype(np.float64))
                self.classifier=classif


                return [None, event_input_value, self.classifier, self.prediction, self.score]

            else:
                classif = data_from_pickle
                self.classifier = classif
                self.prediction=classif.predict(np.array(X_predict).astype(np.float64).reshape(1, -1))
                self.score=classif.score_samples(np.array(X_predict).astype(np.float64).reshape(1, -1))

                return [None, event_input_value, self.classifier, self.prediction, self.score]
