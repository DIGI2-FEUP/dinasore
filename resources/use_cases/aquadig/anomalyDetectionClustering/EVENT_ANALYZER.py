class EVENT_ANALYZER:

    def __init__(self):
        self.classif1=False
        self.behaviour = False
        self.buffer=None
        self.n_max=0


    def schedule(self, event_input_name, event_input_value, classif1, N):

        if event_input_name == 'INIT':
            return [event_input_value, None, self.behaviour, None]

        elif event_input_name == 'RUN':
            if N is None:
                self.n_max = 5
            else:
                self.n_max = N

            if self.buffer is None:
                self.buffer = RingBuffer(self.n_max)

            self.classif1 = bool(int(classif1))

            self.buffer.append(self.classif1)


            if sum(self.buffer.get()) == self.n_max:
                self.behaviour = True
            else:

                self.behaviour = False

        return [None, event_input_value, str(self.behaviour), self.buffer.get()]





class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self,size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max
        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

    def append(self,x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data