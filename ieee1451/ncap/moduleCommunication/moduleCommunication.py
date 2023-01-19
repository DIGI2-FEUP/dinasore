from can_bus.can_dotx import CAN_DOTX
from commands import *
from tim import *
from enum import Enum

from can_bus.can_isotp import *
import moduleCommunication.netComm as netComm
import moduleCommunication.netRegistration as netRegistration
import moduleCommunication.netReceive as netReceive

class CommModuleDot0(netRegistration.NetRegistration, netReceive.NetReceive): # Provided by IEEE 1451.0, called by IEEE 1451.X
    
    def __init__(self, transducerServices):

        self.transducerServices = transducerServices

        self.commModules = []

        self.new_message = threading.Event()
        self.new_message_rcvCommId = 0

    def run(self):
        
        for mod in self.commModules:
            mod.run()

        handle_new_msg = threading.Thread(target = self.handle_new_message)
        handle_new_msg.start()

    def handle_new_message(self):

        while True:
            self.new_message.wait()

            commId = self.new_message_rcvCommId

            commModule = CommModuleDotX.getCommModuleByCommChannel(self.commModules, commId)

            [length, payload, last] = commModule.readMsg(commId, -1, 4095)

            thread = threading.Thread(target = self.handle_new_message_func, args =(payload, commId, commModule))
            thread.start()
            
            self.new_message.clear()

    def handle_new_message_func(self, payload, commId, commModule):

        [channelId, cmdClassId, cmdFunctionId, inArgs] = Codec.decodeCommand(payload)

        if(cmdClassId == 0x80 and cmdFunctionId == 0x01):
            random = inArgs.getByIndex(0).value
            destId = TIM.getNextId()
            payload = DotX_DIGI2.register_response(random, destId)
            commModule.writeRsp(commId, -1, payload, True)
            commModule.close(commId) 

            self.registerDestination(destId, commModule.id)

            
class CommModuleDotX(netComm.NetComm): # Provided by IEEE 1451.X, called by IEEE 1451.0

    nextId = 1

    def __init__(self, commModuleDot0, interfaceType, technologyId, name, id):

        self.commModuleDot0 = commModuleDot0

        self.interfaceType = interfaceType
        self.technologyId = technologyId
        self.name = name
        self.id = id

        self.tims = []
        self.groups = []
        self.commChannels = {}  #commId

        self.wait_events = {}
        self.discovery_done = False

        self.communication_handlers = {}

    def open(self, destId, twoWay):
        commId = CommChannel.getNextId()
        if(destId in self.communication_handlers.keys()):
            communication_handler = self.communication_handlers[destId]
        else: 
            communication_handler = self.openCommunicationHandler(destId)
        while(communication_handler.busy):
            pass
        communication_handler.busy = True
        commChannel = CommChannel(self, communication_handler, destId, commId, twoWay)
        
        self.commChannels[commId] = commChannel

        return [self.commChannels[commId].maxPayloadLen, commId]

    def close(self, commId):        
    #print("Closing a Comm Channel to destId ", self.commChannels[commId].destId)    


        commChannel = self.commChannels[commId]

        commChannel.close()

        commChannel.communication_handler.busy=False

        

        if(commId in self.commChannels.keys()):
            self.commChannels.pop(commId)

    


    def openCommunicationHandler(self,destId):       
        communication_handler = CAN_DOTX(self,1,destId)
        communication_handler.rcvMessage()
        self.communication_handlers[destId] = communication_handler
        return communication_handler

    def closeCommunicationHandler(communication_handler):
        communication_handler.close()


    def run(self):  

        #CAN_DOTX.startSocketlessReception()

        TIM.setNextId(0)
        destId = TIM.getNextId()
        self.commModuleDot0.registerDestination(destId, self.id)
        TIM.setNextId(3)

        self.discoverDestinations()

        nextId = TIM.nextId
        TIM.setNextId(2)
        destId = TIM.getNextId()
        self.commModuleDot0.registerDestination(destId, self.id)
        TIM.setNextId(nextId)

        self.discovery_done = True

    def getNextId():
        print(CommModuleDotX.nextId)
        CommModuleDotX.nextId = CommModuleDotX.nextId + 1
        
        return CommModuleDotX.nextId - 1

    def getCommModule(commModules, commModuleId):

        for x in commModules:
            if(commModuleId == x.id):
                return x
        
        return None

    def getCommModuleByTim(commModules, timId):

        for x in commModules:
            for tim in x.tims:
                if(tim.destId == timId):
                    return x

        return None
    
    def getCommModuleByCommChannel(commModules, commId):

        for x in commModules:
            for commChannel in x.commChannels.values():
                if(commChannel.commId == commId):
                    return x
        
        return None
        
    def getTims(commModules):
        
        tims = []

        for x in commModules:
            for y in x.tims:
                tims.append(y)
        
        return tims

    def addTim(self, tim):

        self.tims.append(tim)
    
    def removeTim(self, tim):

        self.tims.remove(tim)

class CommChannel:

    nextId = 1
    maxPayloadLen = 4095 - 2 # payload = msgId + msgPayload || len(msgId) = 2

    def __init__(self, commModuleDotX, communication_handler, destId, commId, twoWay):

        self.commModuleDotX = commModuleDotX

        self.commId = commId  #commId
        self.destId = destId
        self.twoWay = twoWay

        self.inMessages = []       # Array of Messages
        self.outMessages = []      # Array of Messages

        self.commStatus = Status.Idle

        self.communication_handler = communication_handler


    
    def getNextId():

        CommChannel.nextId = CommChannel.nextId + 1
        
        return CommChannel.nextId - 1

    def getCommChannel(commChannels, commId):

        return commChannels[commId]

    def getCommChannelByOutMsg(commChannels, msgId):

        for x in commChannels.values():
            for msg in x.outMessages:
                if(msg.msgId == msgId):
                    return x
        
        return None

    def sendMessage(self, message):

        payload = message.msgId.to_bytes(2, 'big') + message.payload
        #source = 1         # NCAP Address
        #target = TIM.getTim(self.commModuleDotX.tims, self.destId).address

        if(self.twoWay == True):
            self.communication_handler.rcvMessage()
            self.commModuleDotX.wait_events[message.msgId] = threading.Event()

        #print('Sending Message to ', self.destId)
        if(self.destId == 0) or(self.destId == 2):
            self.communication_handler.sendCANMessage(payload,1,self.destId)
        else:
            self.communication_handler.sendMessage(payload)
    def close(self):
        pass



class Message:

    nextId = 1

    def __init__(self, msgId, payload):
        self.msgId = msgId
        self.payload = payload

        self.index = 0

        self.status = Status.Idle

        self.wait_event = None


    def getNextId():

        Message.nextId = Message.nextId + 1
        
        return Message.nextId - 1


    def getMessage(messages, msgId):

        message = None

        for x in messages:
            if(x.msgId == msgId):
                message = x
        
        return message

    def readMessage(self, maxLen):
        
        if(self.index + maxLen >= len(self.payload)):
            self.index = 0
        else:
            self.index = self.index + maxLen

        return self.payload[self.index:self.index+maxLen]


class InterfaceType(Enum):
    Reserved = 0
    Point2Point = 1
    Network = 2

class Status(Enum):
    Idle = 1
    InitiatorWriting = 2
    InitiatorClosing = 3
    InitiatorReceivePending = 4
    InitiatorReading = 5
    InitiatorAborting = 6
    ReceiverIncomingMsg = 7
    ReceiverReading = 8
    ReceiverWriting = 9
    ReceiverOutgoingMsg = 10
    ReceiverAborting = 11