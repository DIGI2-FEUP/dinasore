import time

class IEEE1451_SENSOR_CONTINUOUS:

    def __init__(self, ncap):
        self.ncap = ncap
        self.previous_time = 0
        self.times_before = []
        self.times_after = []

    def schedule(self, event_name, event_value, tim_id, transducer_id, samp_int):
        
        if event_name == 'INIT':

            if samp_int != None and samp_int > 0:
                self.samp_int = samp_int
            else:
                self.samp_int = 0
            
            return [event_value, None, None]

        if event_name == 'READ':
            
            current_time = time.time_ns()

            if(current_time - self.previous_time > self.samp_int * 1000000):

                #print("Read from tim_id = " + str(tim_id) + " / transducer_id = " + str(transducer_id))

                timId = tim_id
                channelId = transducer_id
                timeout = 10
                samplingMode = 5

                transCommId = self.ncap.transducerServices.open(timId, channelId)
                transducerData = self.ncap.transducerServices.readData(transCommId, timeout, samplingMode)
                self.ncap.transducerServices.close(transCommId)

                value = transducerData.getByIndex(0).value
                self.previous_time = current_time

                return [None, event_value, value[0]]

            return [None, None, None]