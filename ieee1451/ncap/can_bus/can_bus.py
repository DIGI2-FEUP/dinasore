import can

class CANBus:

    def __init__(self):
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        self.set_filters()

    def set_filters(self):
                        [
            {"can_id": 0x18DA0103, "can_mask": 0x1FFFF00, "extended": True},
            {"can_id": 0x18DA0102, "can_mask": 0x1FFFFFF, "extended": True},
        ]

    def sendMessage(self, message, id):
        msg = can.Message(arbitration_id = id, data=message)
        self.bus.send(msg)
    
    def getMessage(self):

        msg = self.bus.recv()
        
        print("Received Message", msg)

        return msg.data

    def readCAN(self):

        while True:
            CANBus.getMessage(self)


if __name__ == '__main__':

        can_bus = CANBus()
        can_bus.getMessage()