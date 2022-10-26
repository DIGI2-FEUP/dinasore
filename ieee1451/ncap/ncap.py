import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'ieee1451/ncap'))
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'ieee1451/diac_integration'))

from applications.webServer import *
from applications.pnpManager import *
from transducerServices.transducerServices import *
from moduleCommunication.moduleCommunication import *
from ieee1451.diac_integration.diac import *
from teds.teds import *

class NCAP:

    def __init__(self, address, port_diac):
        
        self.transducerServices = TransducerServices(self)

        self.pnpManager = PnP_Manager(self)

        if address != None and port_diac != None:
            self.diacManager = DIAC_Manager(address, port_diac)
            self.pnpManager.subscribe(self.diacManager)

        self.webServer = ThreadWebServer(self, '', 8000)

        self.new_transducer_event = threading.Event()
        self.new_transducer = None
        
        self.name = "DIGI2_NCAP"

    def run(self):
        print("Starting NCAP")

        ### Discover Tests ###
        # meas_times.ncap_startup.append(time.time_ns())
        ### -------------- ###

        self.transducerServices.commModuleDot0.registerModule(InterfaceType.Network, 255, "CAN_ISOTP")
        
        self.pnpManager.run()
        self.transducerServices.run()
        self.webServer.run()      


#         geoText = "Hello World"
#        geoText = "<gml:Point srsName=\"urn:ogc:def:crs:OGC:1.3:CRS84\" xmlns:gml=\"http://www.opengis.net/gml\"><gml:pos>100 100</gml:pos></gml:Point>"

#        dirBlock = DirBlock()
#        dirBlock.LangCode = int.from_bytes(b'\x65\x6e', 'big')
#        dirBlock.Length = len(geoText) + 2
#        dirBlock.Offset = 10         # Not Real

#        geoLocTEDS = GeoLoc_TEDS_Data_Block()
#        geoLocTEDS.DirBlock = dirBlock
#        geoLocTEDS.SubSum = 10       # Not Real
#        geoLocTEDS.XMLText = geoText
#        geoLocTEDS.XMLSum = 10       # Not Real

#        t1 = geoLocTEDS.to_argumentArray()
#        t1_str = Codec.argumentArray2Json(t1)

# #        print(t1_str)

#         t2 = geoLocTEDS.to_bytes()

#        teds = TEDS(geoLocTEDS)

#        print(teds.to_bytes().hex())
#         t3 = GeoLoc_TEDS_Data_Block.from_bytes(t2)

#         t3_str = Codec.argumentArray2Json(t3.to_argumentArray())

#        print(t3_str)

#        print(GeoLoc_Util.xmlText2PosXY(t3.XMLText))


        ### Read Tests ###
        # data = input("Please enter the message:\n")
        
        # meas_times = Meas_Times()
        # self.readTC(3, meas_times)
        # meas_times.showResults()

        # meas_times = Meas_Times()
        # meas_times2 = Meas_Times()
        # meas_times3 = Meas_Times()
        # meas_times4 = Meas_Times()
        # thread = threading.Thread(target = self.readTC, args=[3, meas_times])        
        # thread2 = threading.Thread(target = self.readTC, args=[4, meas_times2])     
        # thread3 = threading.Thread(target = self.readTC, args=[5, meas_times3])     
        # thread4 = threading.Thread(target = self.readTC, args=[6, meas_times4])   
        # thread.start()      
        # thread2.start()     
        # thread3.start()     
        # thread4.start()

        # thread.join()
        # thread2.join()
        # thread3.join()
        # thread4.join()
        
        #print(len(meas_times.close_channel))
        #print(len(meas_times.read_service))

        # meas_times.showResults()
        # meas_times2.showResults()
        # meas_times3.showResults()
        # meas_times4.showResults()
        ### ---------- ###

    def readTC(self, id, meas_times):

        timId = id
        channelId = 1
        timeout = 10
        samplingMode = 5

        value = []
        times = []
        meas_times.ff = True

        for i in range(20):
            #print(i)
            time1 = time.time_ns()
            meas_times.read_service.append(time1)
            transCommId = self.transducerServices.open(timId, channelId)
            #meas_times.open_channel.append(time.time_ns())
            transducerData = self.transducerServices.readData(transCommId, timeout, samplingMode)
            #meas_times.return_data.append(time.time_ns())
            self.transducerServices.close(transCommId)
            time2 = time.time_ns()
            meas_times.close_channel.append(time2)

            value.append(transducerData.getByIndex(0).value)
            times.append(time2 - time1)

        # for i in range(20):
        #     print(value[i])

        # for i in range(20):
        #     print(times[i])

    def addTimTransducer(self):

        destId = TIM.getNextId()
        tim = TIM(destId)

        commModule = CommModuleDotX.getCommModule(self.transducerServices.commModuleDot0.commModules, 1)
        commModule.addTim(tim)

        transducer = Transducer(1, "name")
        
        barray = b'\x00\x00\x00\x5f\x03\x04\x00\x03\x01\x01\x0a\x01\x01\x0b\x01\x00\x0c\x06\x32\x01\x00\x39\x01\x82\x0d\x04\x43\x69\x00\x00\x0e\x04\x43\xb0\x80\x00\x0f\x04\x40\x00\x00\x00\x10\x01\x01\x12\x09\x28\x01\x00\x29\x01\x02\x2a\x01\x0c\x14\x04\x3d\xcc\xcc\xcd\x16\x04\x37\xd1\xb7\x17\x17\x04\x3d\xcc\xcc\xcd\x18\x04\x41\xf0\x00\x00\x19\x04\x37\xd1\xb7\x17\x1a\x04\x40\xa0\x00\x00\x1f\x03\x30\x01\x02\xef\x2c'
        teds = TEDS.from_bytes(barray)

        transducer.setTEDS(TEDS_ACCESS_CODES.ChanTEDS, teds)

        tim.addTransducer(transducer)

        while(self.transducerServices.ncap.new_transducer_event.is_set() == True):
            pass

        self.transducerServices.ncap.new_transducer = transducer
        self.transducerServices.ncap.new_transducer_event.set()



if __name__ == '__main__':

    ncapService = NCAP(None, None)
    ncapService.run()
