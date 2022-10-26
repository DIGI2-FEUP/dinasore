import transducerServices.transducerServices as ts
from moduleCommunication.moduleCommunication import *

class TransducerManager:

    def lock(self, transCommId, time_out):
        pass

    def unlock(self, transCommId):
        pass

    def reportLocks(self, transCommIds):
        pass

    def breakLock(self, transCommId):
        pass

    def startCommand(self, transCommId, time_out, cmdClassId, cmdFunctionId, inArgs, callback, operationId):
        pass

    def configureAttributes(self, transCommId, attributeNames):
        pass

    def trigger(self, transCommId, triggerTime, time_out, samplingMode):
        
        commSession = ts.CommSession.getCommSession(self.commSessons, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        for i in len(tims):
            timId = tims[i]
            channelId = channels[i]

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            [maxPayloadLen, commId] = commModule.open(timId, False)

            payload = XdcrOperate(channelId).trigger()

            msgId = Message.getNextId()
            commModule.writeMsg(commId, time_out, payload, True, msgId)

            commModule.close(commId)


    def startTrigger(self, transCommId, triggerTime, time_out, samplingMode, callback, operationId):
        pass

    def clear(self, transCommId, time_out, clearMode):
        pass

    def registerStatusChange(self, transCommId, time_out, callback, operationId):
        pass

    def unregisterStatusChange(self, transCommId):
        pass