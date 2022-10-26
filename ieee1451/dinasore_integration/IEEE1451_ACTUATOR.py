class IEEE1451_ACTUATOR:

    def __init__(self, ncap):
        self.ncap = ncap
    
    def schedule(self, event_name, event_value, tim_id, transducer_id, value):
        
        if event_name == 'INIT':
            return [event_value, None, None]

        if event_name == 'RUN':

            print("Write to tim_id = " + str(tim_id) + " / transducer_id = " + str(transducer_id))

            timId = tim_id
            channelId = transducer_id
            timeout = 10
            samplingMode = 5

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            self.ncap.transducerServices.writeData(self, transCommId, timeout, samplingMode, value)
            self.ncap.transducerServices.close(transCommId)
            
            return [None, event_value]