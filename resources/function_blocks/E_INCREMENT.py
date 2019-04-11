
class E_INCREMENT:

    def schedule(self, event_name, event_value, LIMIT):
        if event_name == 'EI':
            if (LIMIT is None) or (event_value < LIMIT):
                event_value = event_value + 1
                return [event_value]
            else:
                return [None]
