

class ServiceExample:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, rate, signal):
        if event_name == 'Init':
            # print('initialization')
            return [event_value, None, signal + 1]

        elif event_name == 'Run':
            return [None, event_value, signal + 1]
