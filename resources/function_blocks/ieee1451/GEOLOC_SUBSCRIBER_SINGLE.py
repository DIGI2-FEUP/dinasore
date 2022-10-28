class GEOLOC_SUBSCRIBER_SINGLE:

    def __init__(self):
        x = None
        y = None

    def schedule(self, event_name, event_value, x, y, value):
        
        if event_name == 'INIT':
            self.x = x
            self.y = y

            return [event_value, None, None]

        if event_name == 'RUN':

            return [None, event_value, value]