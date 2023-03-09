import datetime


class DATA_ACUM:

    def __init__(self):
        self.buffer = []

    def schedule(self, event_input_name, event_input_value, data, buffer_len):

        if event_input_name == 'INIT':
            self.buffer = []
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            # parses the data
            data2append = data.copy()
            data2append.insert(0, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            # appends the data to the buffer
            self.buffer.append(data2append)
            # checks if the buffer is complete
            if len(self.buffer) < buffer_len:
                # if is not full returns an empty list
                return [None, None, []]
            else:
                # makes a copy of the buffer and clears the buffer
                print(self.buffer)
                buffer_aux = self.buffer.copy()
                self.buffer = []
                # returns the accumulated buffer
                return [None, event_input_value, buffer_aux]
