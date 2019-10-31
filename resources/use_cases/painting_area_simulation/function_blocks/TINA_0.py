from time import sleep


class TINA_0:

    def __init__(self):
        self.material_name = 'not_defined'
        self.container_name = 'not_defined'
        self.actual_state = 0
        self.states_sequence = ['NonUnscheduled', 'Standby', 'Productive', 'Standby']

    def schedule(self, event_name, event_value, material_name, container_name):
        if event_name == 'INIT':
            return [event_value, None, None, None, None,
                    self.material_name, self.container_name,
                    self.states_sequence[self.actual_state]]

        elif event_name == 'READ':

            if self.actual_state == 0:
                self.material_name = 'not_defined'
                self.container_name = 'not_defined'
                sleep(1)
                # returns finishes the cycle
                return [None, event_value, None, None, None,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]

            elif self.actual_state == 1:
                self.material_name = material_name
                self.container_name = container_name
                # waits 2 seconds
                sleep(2)
                # updates the state
                self.actual_state += 1
                # starts the actuators
                return [None, 1, 'CSE', None, None,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]

            elif self.actual_state == 2:
                # waits 10 seconds
                sleep(1)
                # runs in productive loop
                return [None, 1, None, None, None,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]

            elif self.actual_state == 3:
                # waits 1 seconds
                sleep(2)
                # resets the actual state
                self.actual_state = 0
                # returns finishes the cycle
                return [None, event_value, None, None, event_value,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]

        elif event_name == 'SENSORS':
            if event_value == 'CSE':
                # finishes the CSE Process timer
                # starts the Power Wash I
                return [None, None, 'WASH', None, None,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]
            elif event_value == 'WASH':
                # finishes the Power Wash I
                # increments the state
                self.actual_state = 3
                return [None, 1, 'STOP_MEASURING', None, None,
                        self.material_name, self.container_name,
                        self.states_sequence[self.actual_state]]

        elif event_name == 'NEW_MATERIAL':
            # saves the material_name and container_name
            self.material_name = material_name
            self.container_name = container_name
            # updates the state
            self.actual_state += 1
            # returns all the values
            return [None, event_value, None, None, None,
                    self.material_name, self.container_name,
                    self.states_sequence[self.actual_state]]
