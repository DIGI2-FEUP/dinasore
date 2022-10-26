import threading
import time

from can_bus.can_isotp import *

import moduleCommunication.moduleCommunication as mc

class CAN_DOTX:

    def __init__(self):
        pass

    def sendMessage(message, source, target):

        CAN_ISOTP.sendMessage(message, source, target)

    def rcvMessage(commModuleDotX, source, target):

        thread = threading.Thread(target = CAN_ISOTP.rcvMessage, args=(False, CAN_DOTX.handleMessage, source, target, commModuleDotX))
        thread.start()
    
    def handleMessage(commModuleDotX, source, target, payload):

        msgId = int.from_bytes(payload[:2], 'big')

        if(msgId == 0):
            pass
            # TIM Initiated Message (no reply expected)
    
            #print("Received payload on %d %d: %s" % (source, target, payload))
    
        if(msgId > 0x1000 and commModuleDotX.discovery_done == True):

            # TIM Initiated Message (reply Expected)

            [maxPayloadLen, commId] = commModuleDotX.open(target, True)
            commChannel = mc.CommChannel.getCommChannel(commModuleDotX.commChannels, commId)

            msgId = int.from_bytes(payload[:2], 'big')
        
            commChannel.inMessages.append(mc.Message(msgId, payload[2:]))

            length = len(payload[2:])

            commModuleDotX.commModuleDot0.notifyMsg(commId, True, length, length, length, 0)
        
            #print("Received payload on %d %d: %s" % (source, target, payload))
    
        elif(msgId > 0x0000 and msgId < 0x1000):
            # NCAP Initiated Message (reply expected)

            message = mc.Message(msgId, payload[2:])
            commChannel = mc.CommChannel.getCommChannelByOutMsg(commModuleDotX.commChannels, msgId)
            
            commChannel.inMessages.append(message)

            length = len(payload[2:])

            commModuleDotX.commModuleDot0.notifyRsp(commChannel.commId, msgId, length, length, length)

            #print("Received payload on %d %d: %s" % (source, target, payload))
        

if __name__ == '__main__':

    CAN_DOTX.rcvMessage(0x01, 0x02)
    CAN_DOTX.rcvMessage(0x01, 0x03)
    CAN_DOTX.rcvMessage(0x01, 0x04)

    while True:
        pass