class IEEE1451:

    def __init__(self, ncap):
        self.ncap = ncap
        print("4 " + self.ncap.name)
    
    def schedule(self, event_name, event_value, tim_id, transducer_id):
        
        if event_name == 'INIT':
            return [event_value, None, None]

        if event_name == 'RUN':

            print("Read from tim_id = " + str(tim_id) + " / transducer_id = " + str(transducer_id))

            timId = tim_id
            channelId = transducer_id
            timeout = 10
            samplingMode = 5

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            transducerData = self.ncap.transducerServices.readData(transCommId, timeout, samplingMode)
            self.ncap.transducerServices.close(transCommId)
            
            value = transducerData.getByIndex(0).value

            return [None, event_value, value]