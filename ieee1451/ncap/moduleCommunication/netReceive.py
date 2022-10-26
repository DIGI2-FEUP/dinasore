
from moduleCommunication.receive import *

import moduleCommunication.moduleCommunication as mc
import transducerServices.transducerServices as ts

class NetReceive(Receive):

    def abort(self, commId, status):
        pass

    def notifyMsg(self, rcvCommId, twoWay, payloadLen, cacheLen, maxPayloadLen, status):

        while self.new_message.is_set():
            pass
        
        self.new_message_rcvCommId = rcvCommId
        self.new_message.set()
  
    def notifyRsp(self, rcvCommId, msgId, payloadLen, cacheLen, maxPayloadLen):
        
        commModule = mc.CommModuleDotX.getCommModuleByCommChannel(self.commModules, rcvCommId)

        operation = ts.Operation.getOperationByMsgId(self.transducerServices.nb_operations, msgId)

        if(operation != None):
            operation.msgIds.remove(msgId)
            operation.readResponse(rcvCommId, msgId)

            if(len(operation.msgIds) == 0 and operation.complete == True):
                operation.callback(operation.operationId, operation.result, 0)

        else:
            commModule.wait_events[msgId].set()