

class TEST_SERVICE_LIST:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, no_opc_str):
        if event_name == 'INIT':
            return [event_value, None, []]

        elif event_name == 'RUN':
            word_list = no_opc_str.split('_')
            return [None, event_value, word_list]
