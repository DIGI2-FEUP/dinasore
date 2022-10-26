import time
import threading
import logging

from can.interfaces.socketcan.socketcan import *
from can_bus.isotp.protocol import *
from can_bus.isotp.address import *
from can_bus.isotp.errors import *

from ieee1451.ncap.meas_times import *

logger = logging.getLogger('isotp')

class ThreadedCANReception:

    def __init__(self, source, target):
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
            time.sleep(0.00001) # Variable sleep time based on state machine state

    def shutdown(self):
        self.stop()
        CAN_ISOTP.bus.shutdown()


class CAN_ISOTP:

    bus = SocketcanBus(channel='can0')
    addr = Address(AddressingMode.NormalFixed_29bits, source_address=0x01, target_address=0x00)

    stack = CanStack(bus, address=addr)

    def __init__(self):
        pass

    def sendMessage(message, source, target):

        ### Read Tests ###
        # if(message.find(b'\x00\x01\x03\x01\x00\x07\x03\x00\x04\x00\x00\x00\x00') != -1):
        #     #print("here")
        #     Meas_Times.before_send_msg.append(time.time_ns())
        ### ---------- ###

        CAN_ISOTP.stack.send(target, message)
                
        # ### Discover Tests ###
        # if(message.find(b'\x00\x01\x00\x00\x80\x02') != -1):
        #     Meas_Times.send_discover.append(time.time_ns())
        # ### -------------- ###

        

    def rcvMessage(exit_request, callback, source, target, commModuleDotX):

        reception = ThreadedCANReception(source, target)
        reception.start()
        
        payload = []
        while exit_request == False:
            if CAN_ISOTP.stack.available():
                [remote, payload] = CAN_ISOTP.stack.recv()
                
                ### Register Tests ###
                # if(payload.find(b'\x10\x01\x00\x00\x80\x01') != -1):
                #     Meas_Times.message_register.append(time.time_ns())
                ### -------------- ###
                ### Discover Tests ###
                # if(payload.find(b'\x00\x01\x01\x00\x04\x01') == 0):
                #     Meas_Times.discover_response_msg.append(time.time_ns())
                ### -------------- ###
                ### Read Tests ###
                # if(Meas_Times.ff == True):
                #     Meas_Times.after_rcv_msg.append(time.time_ns())
                ### ---------- ###

                thread = threading.Thread(target = callback, args =(commModuleDotX, source, remote, payload))
                thread.start()

        reception.shutdown()

if __name__ == '__main__':

    CAN_ISOTP.sendMessage("Hello World!", 0xAA, 0x55)
    CAN_ISOTP.rcvMessage(0x55, 0xAA)