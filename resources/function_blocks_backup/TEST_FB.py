

class TEST_FB:

    def __init__(self):
        self.G_EI = 0

    def schedule(self, event_name, event_value, G):
        if event_name == 'EI':
            self.G_EI = event_value + 1
            EO1 = None
            return [self.G_EI, EO1]
