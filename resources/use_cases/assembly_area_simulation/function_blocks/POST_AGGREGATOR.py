

class POST_AGGREGATOR:

    def __init__(self):
        self.values_list = []

    def schedule(self, event_name, event_value, input_material1, input_container1,
                 input_material2, input_container2, input_material3, input_container3,
                 input_material4, input_container4, input_material5, input_container5, receive_list):
        if event_name == 'INIT':
            return [None, None, None, '', '', '']

        elif event_name == 'RUN':
            # do nothing
            return [None, None, None, '', '', '']
        elif event_name == 'NEW_MATERIAL':
            values_material = [input_material1, input_material2, input_material3, input_material4, input_material5]
            values_container = [input_container1, input_container2, input_container3, input_container4, input_container5]
            receive_list = receive_list.split(',')
            id_value = receive_list.index(event_value)
            return [None, None, event_value, values_material[id_value], values_container[id_value], receive_list]
        else:
            # the list doesn't have the correct size
            return [None, None, None, '', '', '']
