import can

class CANBus:

    def __init__(self):
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')

    def sendMessage(self, message, id):
        msg = can.Message(arbitration_id = id, data=message)
        self.bus.send(msg)
    
    def getMessage(self):

        msg = self.bus.recv()
        
        return msg.data

        #notifier = can.Notifier(self.bus, [can.Printer()])

    def readCAN(self):

        while True:
            CANBus.getMessage(self)


if __name__ == '__main__':

        can_bus = CANBus()
        can_bus.getMessage()