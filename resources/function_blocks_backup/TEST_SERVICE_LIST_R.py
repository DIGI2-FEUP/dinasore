

class TEST_SERVICE_LIST_R:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, list_str):
        if event_name == 'INIT':
            return [event_value, None]

        elif event_name == 'RUN':
            join_str = ''
            for str_item in list_str:
                join_str += ('_' + str_item)
            return [None, event_value]
