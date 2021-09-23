import numpy as np
import time
import paho.mqtt.client as mqtt
import threading
from random import randrange

class ORCHESTRATOR:

    def available_simulators(self, simuls):

        #print(simuls)

        for x in simuls:
            if (simuls[x] == 0):
                return x

        return None

    def schedule(self, event_name, event_value, register, result, params_in):

        if event_name == 'INIT':
            self.reg_simulator = dict() #state of the simulator
            self.param_simulator = dict()
            self.params = []
            self.counter = 0
            self.counter_results = 1
            self.counter_simulators = 0

            return [None, event_value, None, None,
                    None, None, None, None]

        if event_name == 'READ':

            # allocate new simulator
            simul = self.available_simulators(self.reg_simulator)

            if (simul is None) or (len(self.params) == 0):
                return [None, event_value, None, None,
                        None, None, None, None]
            else:
                #param2send = self.params[self.counter]  # select the correct parameter to send
                #self.counter += 1

                param2send = self.params.pop()

                time.sleep(0.1)

                #self.param_simulator[self.counter] = simul
                self.param_simulator[str(param2send)] = simul
                print("ORCHESTRATOR param sent:", param2send , "counter: " , self.counter)

                self.reg_simulator[simul] = 1  # tag the simulator as executing

                #print("Next allocation: ", simul , param2send)

                return [None, event_value, event_value, None,
                        param2send, simul, None, None]


        if event_name == 'REG': # REGISTER
            # Register simulator
            #self.reg_simulator['/topic/simul_{0}'.format(self.counter_simulators)] = 0

            print("ORCHESTRATOR Registration: " , register)

            self.reg_simulator[register] = 0 #store simulator publish topic a state as idle
            self.counter_simulators += 1

            return [None, None, None, None,
                    None, None, None, None]

        if event_name == 'RESULT_I':

            print("ORCHESTRATOR message init: ", result)
            print("ORCHESTRATOR self.counter_results: ", self.counter_results)
            self.counter_results += 1

            temp_res, temp_param = result.split("_")
            res = eval(temp_res)
            param = eval(temp_param)

            # simulator_done = self.param_simulator[self.params.index(param)]
            simulator_done = self.param_simulator[temp_param]
            # print("simulator: " , simulator_done , " is done")


            self.reg_simulator[simulator_done] = 0  # free the simulator
            print("ORCHESTRATOR message end: ", param)

            return [None, None, None, event_value,
                    None, None, res, param]


        if event_name == 'PARAMS_I': #receiving a batch of paramters, and not only one

            self.params = eval(params_in)

            self.param_simulator = dict()
            self.counter = 0

            return [None, None, None, None,
                    None, None, None, None]



