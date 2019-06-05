

class FastFourierTransform:

    def __init__(self):
        pass

    def schedule(self, event_name, event_value, value):
        if event_name == 'Init':
            print('initialization')
            return [event_value, None, value + 1]

        elif event_name == 'Run':
            print('run')
            return [None, event_value, value + 1]
