import numpy as np
import pandas as pd
import scipy.optimize as optimize
import re
import os
from sklearn.preprocessing import StandardScaler


class OPTIMIZE_MODELS:

    def __init__(self):
        self.Nfeval=1
        self.temp = 5230
        self.title_to_df=""
        self.call_back_matrix=[]

    def schedule(self, event_input_name, event_input_value, alpha, model1, model1_up, model2, model2_up, lw, up, verbose, temp):
        def callbackF(x, f, context):

            # USAR SE FOR PARA IMPRIMIR NO TERMINAL
            """
            ##creates the title string containing the x[i] and prints it if running optimization for the first time
            if (self.Nfeval == 1) :

                title='Nfeval\t\t x0'
                for i in range(len(x)-1):
                    title=title+'\t\t\t\tx{0:d}'.format(i+1)
                title = title + '\t\t\t\tf(x)'
                print(title)

            #prints the current minimum
            iteraction='{0: d}'.format(self.Nfeval)
            for i in range(len(x) ):
                iteraction=iteraction+'\t\t{0: 3.6f}'.format(x[i])
            iteraction=iteraction+'\t\t{0: 3.6f}'.format(f[0])
            print(iteraction)
            self.Nfeval=self.Nfeval+1
            """


            # USAR SE FOR PARA FB
            #saves a matrix with the current minimum
            iteraction=np.hstack((x,f[0]))

            # initializes the dataframe with the corresponding title
            if (self.Nfeval == 1) :

                self.title_to_df =['x0']
                for i in range(len(x)-1):
                    self.title_to_df=self.title_to_df+['x{0:d}'.format(i+1)]
                self.title_to_df = self.title_to_df + ['f(x)']
                self.call_back_matrix=pd.DataFrame([iteraction], columns=self.title_to_df)

            self.call_back_matrix = self.call_back_matrix.append (pd.DataFrame([iteraction], columns=self.title_to_df), ignore_index=True)
            self.Nfeval = self.Nfeval + 1

        if event_input_name == 'INIT':
            return [event_input_value, None, [], []]

        elif event_input_name == 'RUN':
            # Initializes upper bound of both models, if not specified
            if model1_up is None:
                model1_up = 1
            if model2_up is None:
                model2_up = 1

            # resets callback history
            self.call_back_matrix = []

            # defines function to optimize, considering two models
            func = lambda X: alpha * (model1.predict(X.reshape(1, -1)) / model1_up) ** 2 + (1 - alpha) * (
                        model2.predict(X.reshape(1, -1)) / model2_up) ** 2

            # chooses temperature if any value were provided
            if temp is not None:
                self.temp = temp

            # chooses the callback function or not
            if verbose:
                res = optimize.dual_annealing(func, callback=callbackF, bounds=list(zip(np.array(eval(lw)), np.array(eval(up)))),
                                              initial_temp=self.temp)
            else:
                res = optimize.dual_annealing(func, bounds=list(zip(np.array(eval(lw)), np.array(eval(up)))), initial_temp=self.temp)

            # resets the evaluantions counter
            self.Nfeval = 1


            return [None, event_input_value, res, self.call_back_matrix]