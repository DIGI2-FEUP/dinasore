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

                # time1 = time.time_ns()
                transCommId = self.ncap.transducerServices.open(timId, channelId)
                transducerData = self.ncap.transducerServices.readData(transCommId, timeout, samplingMode)
                self.ncap.transducerServices.close(transCommId)
                # time2 = time.time_ns()

                ### Read Tests ###
                # self.times_before.append(time1)
                # self.times_after.append(time2)

                # if(len(self.times_before) == 20):
                #     time.sleep((timId - 2) * 3)
                #     print("Read Service -- Close Channel")
                #     for i in range(20):
                #         value = self.times_after[i] - self.times_before[i]
                #         print(value)

                #     print("Between Reads")
                #     for i in range(19):
                #         value = self.times_before[i + 1] - self.times_before[i]
                #         print(value)
                ### ----------- ###

                value = transducerData.getByIndex(0).value
                self.previous_time = current_time

                return [None, event_value, value[0]]

            return [None, None, None]