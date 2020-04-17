import numpy as np


class GROUPING:
    def __init__(self):
        self.data_in = []
        self.width = 0
        self.grouped_data = []
        self.step = 0
        self.size=[]

    def schedule(self, event_name, event_value, Feature_column, Width):

        if event_name == 'INIT':

            return [event_value, None, self.grouped_data, self.size]

        elif event_name == 'RUN':
            # assigns a width: given by the user or 20, by default
            if Width is None:
                self.width = 20
            else:
                self.width = Width

            # defines the step: how many values to jump, each new line
            self.step = int(self.width / 4)

            # inverte a coluna de data, para ficar com a info mais recente em cima, caso tenha de descartar elementos
            self.data_in = Feature_column[-1:-len(Feature_column) - 1:-1]

            # creates the groups for each line
            for i in np.arange(0, len(Feature_column) - self.step + 2, self.step):

                ans = np.copy(self.data_in[i:(self.width + i)])
                if ans.size < self.width:
                    break;

                if len(ans) == self.width:
                    if len(self.grouped_data) == 0:
                        self.grouped_data = np.copy(ans).reshape((1, self.width))
                    else:
                        self.grouped_data = np.vstack((self.grouped_data, ans.reshape((1, self.width))))

            # flips the data, so that chronological order is mantained
            self.grouped_data = np.flip(self.grouped_data)

            # evaluates the shape of the output matrix
            self.size = self.grouped_data.shape
            return [None, event_value, self.grouped_data, self.size]
