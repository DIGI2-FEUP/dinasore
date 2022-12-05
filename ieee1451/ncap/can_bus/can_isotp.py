import time
import threading
import logging

from can.interfaces.socketcan.socketcan import *
from can_bus.isotp.protocol import *
from can_bus.isotp.address import *
from can_bus.isotp.errors import *

#from ieee1451.ncap.meas_times import *

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
        CAN_ISOTP.stack.send(target, message)
                

    def rcvMessage(exit_request, callback, source, target, commModuleDotX):

        reception = ThreadedCANReception(source, target)
        reception.start()
        
        payload = []
        while exit_request == False:
            if CAN_ISOTP.stack.available():
                [remote, payload] = CAN_ISOTP.stack.recv()

                thread = threading.Thread(target = callback, args =(commModuleDotX, source, remote, payload))
                thread.start()

        reception.shutdown()