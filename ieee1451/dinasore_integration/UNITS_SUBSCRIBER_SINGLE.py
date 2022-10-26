class UNITS_SUBSCRIBER_SINGLE:

    def __init__(self):
        units = None

    def schedule(self, event_name, event_value, units, value):
        
        if event_name == 'INIT':
            self.units = units

            return [event_value, None, None]

        if event_name == 'RUN':

            return [None, event_value, value]