

class DATA_PARSER:

    def __init__(self):
        pass

    def schedule(self, event_input_name, event_input_value, data):

        if event_input_name == 'INIT':
            return [event_input_value, None, []]

        elif event_input_name == 'RUN':
            # checks if msg contains a sample
            if data == '':
                # if is not full returns an empty list
                return [None, None, []]
            # parses the data
            data_parsed = []
            for v in data.split(','):
                data_parsed.append(v)
            # returns the parsed data
            return [None, event_input_value, data_parsed]
