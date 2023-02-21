

class WRITE_CSV:

    def __init__(self):
        pass

    def schedule(self, event_input_name, event_input_value, data, path):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':

            if path is None:
                return [None, event_input_value, "Error in specifying path"]

            if data is None:
                return [None, event_input_value, "No data received"]

            print("Data on write CSV:", data)

            with open(path, "a+") as f:
                f.write(data)

            return [None, event_input_value, "OK"]
