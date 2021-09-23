import threading
import random
from time import sleep
from datetime import datetime


class BUFFER:

    def __init__(self):
        self.material_name = 'not_defined'
        self.container_name = 'not_defined'
        self.actual_state = 0
        self.states_sequence = ['NotFull', 'Full']
        self.event = 1
        self.first = True
        self.proceed = 0
        self.sync = 0
        self.buffer_id = 0
        self.buffer_size = 0
        self.buffer = []

    def schedule(self, event_name, event_value, material_name, container_name, buffer_id, buffer_size):

        if event_name == 'INIT':
            print("init")
            self.buffer_id = buffer_id
            self.buffer_size = buffer_size
            return [event_value, None, None, None, None, None, None, None, self.states_sequence[self.actual_state]]

        elif event_name == 'SYNC':
            sleep(5)
            print("sync: buffer: ", self.buffer)
            if len(self.buffer) > 0:
                first_element = self.buffer.pop(0)
                # self.sync += 1
                self.proceed -= 1
                return [None, None, self.sync, None, None, 'NEW_MATERIAL',
                        first_element[0], first_element[1],
                        self.states_sequence[self.actual_state]]
            else:
                self.proceed += 1
                return [None, None, self.sync, None, None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]

        elif event_name == 'NEW_MATERIAL':
            self.material_name = material_name
            self.container_name = container_name

            ##################################################
            # Add element to stack
            ##################################################
            self.buffer.append((material_name, container_name))
            ##################################################
            if self.buffer_size == 0 or len(self.buffer) < self.buffer_size:
                self.actual_state = 0
                self.sync += 1
                if self.first or self.proceed > 0:
                    self.first = False
                    if self.proceed > 0:
                        self.proceed -= 1
                    first_element = self.buffer.pop(0)
                    return [None, None, self.sync, None, None, event_value,
                            first_element[0], first_element[1],
                            self.states_sequence[self.actual_state]]
                else:
                    return [None, None, self.sync, None, None, None,
                            None, None,
                            self.states_sequence[self.actual_state]]

            else:
                self.actual_state = 1
                return [None, None, None, None, None, None,
                        None, None,
                        self.states_sequence[self.actual_state]]
        else:
            return [None, None, None, None, None, None,
                    None, None,
                    self.states_sequence[self.actual_state]]
