from moduleCommunication.moduleCommunication import *
from util import *

from . import tedsManager
from . import timDiscovery 
from . import transducerAccess
from . import transducerManager
from . import commManager
from . import appCallback

class TransducerServices(timDiscovery.TimDiscovery, transducerAccess.TransducerAccess, 
    transducerManager.TransducerManager, tedsManager.TedsManager, 
    commManager.CommManager):

    def __init__(self, ncap):

        self.ncap = ncap
        
        self.commSessions = []  #transCommId

        self.commModuleDot0 = CommModuleDot0(self)

        self.nb_operations = []  # Non-blocking Operations      [operationId, cmd, callback function]

    def run(self):

        print("Starting Transducer Services")
        self.commModuleDot0.run()


class CommSession:

    nextId = 1

    def __init__(self, transCommId, tim, channel):

        self.tims = []
        self.tims.append(tim)
        self.tims = flatten(self.tims)
        self.channels = []
        self.channels.append(channel)
        self.channels = flatten(self.channels)

        self.transCommId = transCommId     #transCommId


    def getNextId():

        CommSession.nextId = CommSession.nextId + 1
        
        return CommSession.nextId - 1


    def getCommSession(commSessions, timId, channelId):

        channel = None
        
        for x in commSessions:
            for y in range(x.n):
                if((x.tim[y] == timId) and (x.channel[y] == channelId)):
                    channel = x

        return channel.id

    def getCommSession(commSessions, transCommId):

        session = None

        for x in commSessions:
            if(x.transCommId == transCommId):
                session = x
        
        return session

    def close(self):
        pass

class Operation:

    nextId = 1

    def __init__(self, operationId, type, callback):
        self.operationId = operationId
        self.type = type                                       # 0 - startRead, 1 - startWrite, 2 - startStream
        self.callback = callback

        self.msgIds = []

        self.complete = False
        self.result = ArgumentArray()

    def getNextId():

        Operation.nextId = Operation.nextId + 1
        
        return Operation.nextId - 1

    def getOperationByMsgId(operations, msgId):

        for oper in operations:
            if(msgId in oper.msgIds):
                return oper

        return None

    def getOperationById(operations, id):

        for oper in operations:
            if(oper.operationId == id):
                return oper

        return None
    
    def readResponse(self, commId, msgId):

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)

            [successFlag, outArgs] = Codec.decodeResponse(payload)
            
            offset = outArgs.getByIndex(0)
   
            if(offset.value < 2**32 - 1):
                sensorData = outArgs.getByIndex(1)
                self.result.putByName("result", Argument(sensorData.typeCode, sensorData.value))

            commModule.close(commId)