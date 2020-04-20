import numpy as np


class FEATURE_EXTRACTION:

    def __init__(self):
        self.data_in = []
        self.data_out = []
        self.width = 0
        self.size = []
        self.ndim = 0

    def schedule(self, event_input_name, event_input_value, data_in):
        if event_input_name == 'INIT':

            return [event_input_value, None, self.data_out, self.size]

        elif event_input_name == 'RUN':
            self.data_in = np.copy(data_in)
            #evaluates the number of dimensions of the inputted data. If it is a line, behaves as follow. If it is a matrix, see "else:"
            if self.data_in.ndim == 1:
                #calculates the number of measurements per line
                self.width = len(self.data_in)

                #calculates the mean values for the: entire window, half window and a quarter of window (takes the most recent values)
                mean_x = np.mean(self.data_in[-1: (-self.width - 1):-1])
                mean_x_2 = np.mean(self.data_in[-1: (-int(self.width / 2) - 1):-1])
                mean_x_4 = np.mean(self.data_in[-1: (-int(self.width / 4) - 1):-1])

                #calculates the std values for the: entire window, half window and a quarter of window (takes the most recent values)
                std_x = np.std(self.data_in[-1: (-self.width - 1):-1])
                std_x_2 = np.std(self.data_in[-1: (-int(self.width / 2) - 1):-1])
                std_x_4 = np.std(self.data_in[-1: (-int(self.width / 4) - 1):-1])

                #creates the data to be outputted, an np array with 6 columns. In this case, the output will have shape of be (1, 6)
                self.data_out = np.array([mean_x, mean_x_2, mean_x_4, std_x, std_x_2, std_x_4])

                #calculates the shape of the output
                self.size = self.data_out.shape

            else:
                #calculates the number of measurements per line
                self.width = len(data_in[0])

                #evaluates the stats for each line. In other words, takes a sample and extracts 6 new features

                for vector in data_in:
                    # calculates the mean values for the: entire window, half window and a quarter of window (takes the most recent values)
                    mean_x = np.mean(vector[-1: (-self.width - 1):-1])
                    mean_x_2 = np.mean(vector[-1: (-int(self.width / 2) - 1):-1])
                    mean_x_4 = np.mean(vector[-1: (-int(self.width / 4) - 1):-1])

                    # calculates the std values for the: entire window, half window and a quarter of window (takes the most recent values)
                    std_x = np.std(vector[-1: (-self.width - 1):-1])
                    std_x_2 = np.std(vector[-1: (-int(self.width / 2) - 1):-1])
                    std_x_4 = np.std(vector[-1: (-int(self.width / 4) - 1):-1])

                    # creates the line (sample) with 6 columns
                    ans = np.array([mean_x, mean_x_2, mean_x_4, std_x, std_x_2, std_x_4])

                    #creates or appends data to the output vector
                    if len(self.data_out) == 0:
                        self.data_out = np.copy(ans)
                        #print(self.data_out)
                    else:
                        self.data_out = np.vstack((self.data_out, ans))

                # calculates the shape of the output
                self.size = self.data_out.shape


            return [None, event_input_value, self.data_out, self.size]