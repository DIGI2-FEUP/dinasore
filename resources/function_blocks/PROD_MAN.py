

class PROD_MAN:

    def __init__(self):
        self.state = 'IDLE'

    def schedule(self, event_name, event_value):

        if event_name == 'INIT':
            self.state = 'IDLE'
            return [event_value, None, 'IDLE']

        elif event_name == 'ON-OFF':
            # switches the button
            if self.state == 'IDLE':
                # updates the data
                self.state = 'WORK'
                return [None, event_value, self.state]
            else:
                self.state = 'IDLE'
                return [None, event_value, self.state]
