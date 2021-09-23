import requests
import json
import time
import numpy as np

class SENSOR_DB_SIM:


    def __init__(self):
        self.t_cycle=""
        self.measurement=0
        self.ok=False
        self.dist=[]
        self.counter=0

    def schedule(self, event_name, event_value, MEAN, STD, SIZE, T_CYCLE):

        if event_name == 'INIT':
            return [None, None, None, 0.0, -1, False]

        elif event_name == 'READ':
            if self.counter == SIZE:
                self.ok=True
                return [None, event_value, None, self.measurement, self.counter, self.ok]


            time.sleep(T_CYCLE)
            self.measurement=self.dist[self.counter]
            self.counter+=1

            return [None, event_value, None,  self.measurement, self.counter, self.ok]

        elif event_name == 'CAPTURE':
            self.dist=np.random.normal(MEAN, STD, SIZE)

            return [None,  event_value, None, None, -1, self.ok]