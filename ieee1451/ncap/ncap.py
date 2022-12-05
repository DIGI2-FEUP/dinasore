import sys
import os
from multiprocessing import Process

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'ieee1451/ncap'))
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'ieee1451/diac_integration'))

from applications.webServer import *
from applications.pnpManager import *
from transducerServices.transducerServices import *
from moduleCommunication.moduleCommunication import *
from ieee1451.diac_integration.diac import *
from teds.teds import *

class NCAP:

    def __init__(self, ncap_address, port_diac, diac_address, project_name):
        
        self.transducerServices = TransducerServices(self)

        self.pnpManager = PnP_Manager(self)

        if diac_address != None and project_name != None:
            self.diacManager = DIAC_Manager(ncap_address, port_diac, diac_address, project_name)
            self.pnpManager.subscribe(self.diacManager)

        self.webServer = ThreadWebServer(self, '', 8000)

        self.new_transducer_event = threading.Event()
        self.new_transducer = None
        
        self.name = "DIGI2_NCAP"

    def run(self):
        print("Starting NCAP")

        self.transducerServices.commModuleDot0.registerModule(InterfaceType.Network, 255, "CAN_ISOTP")
        
        #self.pnpManager.run()
        p1 = Process(target=  self.pnpManager.run(), args=(1,))
        p1.start()
        #self.transducerServices.run()
        p2 = Process(target= self.transducerServices.run(), args=(1,))
        p2.start()

        p3 = Process(target= self.webServer.run(), args=(1,))
        p3.start()
        #self.webServer.run()      

if __name__ == '__main__':

    ncapService = NCAP(None, None)
    ncapService.run()
