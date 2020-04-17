from sklearn.covariance import EllipticEnvelope
import numpy as np

class ELLIP_ENVELOPE:

    def __init__(self):
        self.classifier=None
        self.prediction=None
        self.score=None
        self.predict_proba=None

        self.store_precision=True
        self.assume_centered=False
        self.support_fraction=None
        self.contamination=0.1
        self.random_state=None


    def schedule(self, event_input_name, event_input_value, data_from_pickle, X_predict, X_train, y_train,
                 store_precision, assume_centered, support_fraction, contamination, random_state):

        if event_input_name == 'INIT':

            return [event_input_value, None, self.classifier, self.prediction, self.score]

        elif event_input_name == 'RUN':
            if data_from_pickle == None:
                # default values or not
                if store_precision is not None:
                    self.store_precision = store_precision
                if assume_centered is not None:
                    self.assume_centered = assume_centered
                if support_fraction is not None:
                    self.support_fraction = support_fraction
                if contamination is not None:
                    self.contamination = contamination
                if random_state is not None:
                    self.random_state = random_state

                classif = EllipticEnvelope( )

                classif.fit(np.array(X_train).astype(np.float64), np.array(y_train).astype(np.float64))
                self.classifier=classif


                return [None, event_input_value, self.classifier, self.prediction, self.score]

            else:
                classif = data_from_pickle
                self.classifier = classif
                self.prediction=classif.predict(np.array(X_predict).astype(np.float64).reshape(1, -1))
                self.score=classif.score_samples(np.array(X_predict).astype(np.float64).reshape(1, -1))

                return [None, event_input_value, self.classifier, self.prediction, self.score]
