

class MOVING_AVERAGE:

    def __init__(self):
        self.values_list = []

    def schedule(self, event_name, event_value, window, value):
        if event_name == 'INIT':
            return [event_value, None, 0]

        elif event_name == 'RUN':
            # appends the value to the list
            self.values_list.append(value)
            # checks the size of the list
            if len(self.values_list) == window:
                # calculate the moving average
                moving_average = sum(self.values_list)/window
                # removes the last value
                self.values_list.pop(0)
                # returns the moving average value
                return [None, event_value, moving_average]
            else:
                # the list doesn't have the correct size
                return [None, None, 0]
