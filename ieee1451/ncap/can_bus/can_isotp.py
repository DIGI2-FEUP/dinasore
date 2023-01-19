import time
import threading
import logging

from can.interfaces.socketcan.socketcan import *
from can_bus.protocol_socketless import *
from can_bus.address_socketless import *
from can_bus.isotp.errors import *


#from ieee1451.ncap.meas_times import *

logger = logging.getLogger('isotp')

class ThreadedCANReception:

    def __init__(self):
        self.exit_requested = False

    def start(self):
        self.exit_requested = False
        self.thread = threading.Thread(target = self.thread_task)
        self.thread.start()

    def stop(self):
        self.exit_requested = True
        if self.thread.is_alive():
            self.thread.join()

    def my_error_handler(self, error):
        logging.warning('IsoTp error happened : %s - %s' % (error.__class__.__name__, str(error)))

    def thread_task(self):
        while self.exit_requested == False:
            CAN_ISOTP.stack.process()                # Non-blocking
            time.sleep(0.010)

    def shutdown(self):
        self.stop()
        CAN_ISOTP.bus.shutdown()


class CAN_ISOTP:

    bus = SocketcanBus(channel='can0')
    addr = Address_Socketless(AddressingMode.NormalFixed_29bits, source_address=0x01, target_address=0x00)

    stack = CanStack(bus, address=addr)
    i=0
    filters = []
    for i in range(0,255,1):
        filters.append({"can_id": 0x18DA0100 | i, "can_mask": 0x1FFFFFFF, "extended": True})
    bus.set_filters(filters = filters)

    def sendMessage(message, source, target):
        CAN_ISOTP.stack.send(target, message)             

    def filter_out_destination(source):
        #print("Excluded ", source, "from CAN socketless Reception")
        CAN_ISOTP.filters.remove({"can_id": (0x18DA0100 | source), "can_mask": 0x1FFFFFFF, "extended": True})
        CAN_ISOTP.bus.set_filters(CAN_ISOTP.filters)

    def add_destination(source): 
        CAN_ISOTP.filters.append({"can_id": (0x18DA0100 | source), "can_mask": 0x1FFFFFFF, "extended": True})
        CAN_ISOTP.bus.set_filters(CAN_ISOTP.filters)
'''
    def rcvIsoTPMessage(commModuleDotX, source, target):
        
        s = isotp.socket()
        # Configuring the sockets.
        s.set_fc_opts(stmin=5, bs=10)

        message = None
        #print(source, target)
        addr = Address(AddressingMode.NormalFixed_29bits, source_address=target, target_address=source)

        #print(addr.get_rx_arbitraton_id())
        s.bind("can0", address = addr)

        message = s.recv()
        while( message==None ):
           message=s.recv()
        #print('Sent new', s.address.target_address)
        s.close()
        return message
        

    '''