import numpy as np
import numpy as np
from sklearn.cluster import KMeans


class KMEANS:
    def __init__(self):
        self.full_data=[]
        self.prediction=False
        self.n_clusters = 8
        self.init = 'k-means++'
        self.n_init = 10
        self.max_iter = 300
        self.tol = 0.0001
        self.precompute_distances = 'auto'
        self.verbose = 0
        self.random_state = None
        self.copy_x = True
        self.n_jobs = None
        self.algorithm = 'auto'
        self.results=[]

    def schedule(self, event_input_name, event_input_value, data_in, n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs, algorithm):
        if event_input_name == 'INIT':
            return [event_input_value, None, self.prediction]

        elif event_input_name == 'RUN':
            self.full_data = np.copy(data_in)

            # default values or not
            if n_clusters is not None:
                self.n_clusters = int(n_clusters)
            if init is not None:
                self.init = init
            if n_init is not None:
                self.n_init = int(n_init)
            if max_iter is not None:
                self.max_iter = int(max_iter)
            if tol is not None:
                self.tol = float(tol)
            if precompute_distances is not None:
                self.precompute_distances = precompute_distances
            if verbose is not None:
                self.verbose = int(verbose)
            if random_state is not None:
                self.random_state = int(random_state)
            if copy_x is not None:
                self.copy_x = copy_x
            if n_jobs is not None:
                self.algorithm = algorithm

            kmeans_results = KMeans(n_clusters=self.n_clusters, init=self.init, n_init=self.n_init,
                                    max_iter=self.max_iter, tol=self.tol,
                                    precompute_distances=self.precompute_distances, verbose=self.verbose,
                                    random_state=self.random_state,
                                    copy_x=self.copy_x, n_jobs=self.n_jobs, algorithm=self.algorithm).fit_predict(
                self.full_data)

            self.results = np.copy(kmeans_results)
            self.prediction = self.results[-1]
            # print(kmeans_results.labels_)

            return [None, event_input_value, self.prediction]