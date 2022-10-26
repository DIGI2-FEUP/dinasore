class IEEE1451_EVENT_SENSOR:

    def __init__(self, ncap):
        self.ncap = ncap
        self.previous_value = 0
    
    def schedule(self, event_name, event_value, tim_id, transducer_id):
        
        if event_name == 'INIT':            
            return [event_value, None, None, None]

        if event_name == 'READ':
            
            print("Read from tim_id = " + str(tim_id) + " / transducer_id = " + str(transducer_id))

            timId = tim_id
            channelId = transducer_id
            timeout = 10
            samplingMode = 5

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            transducerData = self.ncap.transducerServices.readData(transCommId, timeout, samplingMode)
            self.ncap.transducerServices.close(transCommId)
            
            value = transducerData.getByIndex(0).value
            
            ris_edge = None
            fal_edge = None
            
            if(self.previous_value == 0 and value == 1):
                ris_edge = event_value
            elif(self.previous_value == 1 and value == 0):
                fal_edge = event_value

            self.previous_value = value

            return [None, event_name, ris_edge, fal_edge]