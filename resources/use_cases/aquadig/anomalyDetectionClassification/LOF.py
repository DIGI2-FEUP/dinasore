from sklearn.neighbors import LocalOutlierFactor
import numpy as np

class LOF:

    def __init__(self):
        self.classifier=None
        self.prediction=None
        self.score=None
        self.score_samples=None

        self.n_neighbors=20
        self.algorithm='auto'
        self.leaf_size=30
        self.metric='minkowski'
        self.p=2
        self.metric_params=None
        self.contamination='auto'
        self.novelty=False
        self.n_jobs=None


    def schedule(self, event_input_name, event_input_value,  data_from_pickle, X_predict, X_train, y_train,
                 n_neighbors, algorithm, leaf_size, metric, p, metric_params, contamination, novelty, n_jobs):

        if event_input_name == 'INIT':

            return [event_input_value, None,self.classifier, self.prediction, self.score_samples]

        elif event_input_name == 'RUN':

            if data_from_pickle == None:
                # default values or not
                if n_neighbors is not None:
                    self.n_neighbors = int(n_neighbors)
                if algorithm is not None:
                    self.algorithm = algorithm
                if leaf_size is not None:
                    self.leaf_size = int(leaf_size)
                if metric is not None:
                    self.metric = metric
                if p is not None:
                    self.p = int(p)
                if metric_params is not None:
                    self.metric_params = metric_params
                if contamination is not None:
                    if contamination == 'auto':
                        self.contamination='auto'
                    else:
                        self.contamination=float(contamination)
                if novelty is not None:
                    self.novelty=novelty
                if n_jobs is not None:
                    self.n_jobs = int(n_jobs)

                classif = LocalOutlierFactor(n_neighbors=self.n_neighbors, algorithm=self.algorithm, leaf_size=self.leaf_size,
                                           metric=self.metric, p=self.p, metric_params=self.metric_params,
                                           contamination=self.contamination, novelty=self.novelty, n_jobs=self.n_jobs)

                classif.fit(np.array(X_train).astype(np.float64), np.array(y_train).astype(np.float64))
                self.classifier=classif

                return [None, event_input_value, self.classifier, self.prediction, self.score_samples]
            else:
                classif = data_from_pickle
                self.classifier = classif
                self.prediction=classif.predict(np.array(X_predict).astype(np.float64).reshape(1, -1))
                self.score_samples=classif.score_samples(np.array(X_predict).astype(np.float64).reshape(1, -1))

                return [None, event_input_value, self.classifier,  self.prediction, self.score_samples]