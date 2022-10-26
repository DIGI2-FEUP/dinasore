import threading

class PnP_Manager:
    
    def __init__(self, ncap):

        self.ncap = ncap
        self.subscribers = []

    def run(self):
        print("Starting PnP Manager")
        self.exit_request = False
        self.thread = threading.Thread(target = self.run_task, daemon = True)
        self.thread.start()

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def notifySubscriber(self, transducer):
        for subs in self.subscribers:
            subs.update(transducer)

    def run_task(self):

        while True:
            self.ncap.new_transducer_event.wait()
            self.ncap.new_transducer_event.clear()

            transducer = self.ncap.new_transducer
            self.ncap.new_transducer = None

            self.notifySubscriber(transducer)