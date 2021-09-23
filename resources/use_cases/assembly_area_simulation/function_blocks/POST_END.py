import threading
import random
from time import sleep
from datetime import datetime


class POST_END:

    def __init__(self):
        self.material_name = 'not_defined'
        self.container_name = 'not_defined'
        self.actual_state = 0
        self.states_sequence = ['NonUnscheduled', 'Standby', 'Productive', 'Standby', 'Error', 'Standby']
        self.event = 1
        self.sync = 0
        self.name = threading.currentThread().getName()

    def writeFile(self):
        the_file = open('somefile.txt', 'a')
        the_file.write("{0},{1},{2},{3}\n".format(threading.currentThread().getName(), self.material_name, self.container_name, datetime.now()))
        the_file.close()

    def schedule(self, event_name, event_value, material_name, container_name, fault_prob):


        if event_name == 'INIT':
            return [event_value, None, None, None, None, None,
                    self.material_name, self.container_name,
                    self.states_sequence[self.actual_state]]

        elif event_name == 'READ':

            # returns finishes the cycle #NonUnscheduled
            if self.actual_state == 0:
                self.material_name = 'not_defined'
                self.container_name = 'not_defined'
                sleep(1)
                # returns finishes the cycle #NonUnscheduled
                return [None, None, None, None, None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

            # Standby
            elif self.actual_state == 1:
                self.material_name = material_name
                self.container_name = container_name

                ##################################################
                self.writeFile()
                ##################################################

                # waits 2 seconds
                sleep(2)
                # updates the state
                self.actual_state += 1
                # starts the actuators
                return [None, 1, None, 'CSE', None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

            # Productive wait for CSE
            elif self.actual_state == 2:
                # waits 10 seconds
                #sleep(0.1)
                # runs in productive loop
                return [None, None, None, None, None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

            # Standby injecting error or moving to final state
            elif self.actual_state == 3:

                if random.randint(0, 100) < fault_prob:
                    self.actual_state += 1
                    # Injects an error and waits for error response
                    return [None, None, None, 'ERROR', None, None,
                            None, None,
                            self.states_sequence[self.actual_state]]
                else:
                    self.actual_state = 5
                    # runs in productive loop
                    return [None, 1, None, None, None, None,
                            None, None,
                            self.states_sequence[self.actual_state]]

            # Productive waiting for Error state
            elif self.actual_state == 4:
                #sleep(0.1)
                # runs in productive loop
                return [None, None, None, None, None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

            elif self.actual_state == 5:
                # waits 1 seconds
                sleep(2)
                # resets the actual state
                self.actual_state = 0
                self.sync += 1
                # returns finishes the cycle
                return [None, None, self.sync, None, None, self.event,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]



        elif event_name == 'SENSORS':
            if event_value == 'CSE':
                # finishes the CSE Process timer
                # starts the Power Wash I
                self.actual_state = 3
                return [None, 1, None, 'STOP_MEASURING', None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

            elif event_value == 'ERROR':
                # finishes the CSE Process timer
                # starts the Error
                self.actual_state = 5
                return [None, 1, None, 'STOP_MEASURING', None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

        # standby
        elif event_name == 'NEW_MATERIAL':
            # saves the material_name and container_name
            self.material_name = material_name
            self.container_name = container_name
            self.event = event_value
            # updates the state

            # updates the state
            if self.actual_state != 0:
                # returns all the values
                return [None, None, None, None, None, None,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]
            else:
                self.actual_state = 1
            # returns all the values
            return [None, event_value, None, None, None, None,
                    None, None,
                    self.states_sequence[self.actual_state]]
