import transducerServices.transducerServices as ts
from moduleCommunication.moduleCommunication import *

class TransducerAccess:
    
    def open(self, timId, channelId):
        
        transCommId = ts.CommSession.getNextId()

        self.commSessions.append(ts.CommSession(transCommId, timId, channelId))

        return transCommId

    def openQoS(self, timId, channelId, qosParams, transCommId):
        pass

    def openGroup(self, timIds, channelIds):
        
        transCommId = ts.CommSession.getNextId()

        self.commSessions.append(ts.CommSession(transCommId, timIds, channelIds))

        return transCommId

    def openGroupQoS(self, timIds, channelsIds, transCommId):
        pass

    def close(self, transCommId):

        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        commSession.close()

        self.commSessions.remove(commSession)


    def readData(self, transCommId, time_out, samplingMode):

        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        result = ArgumentArray()

        for i in range(len(tims)):
            timId = tims[i]
            channelId = channels[i]

            # # ------- Change Sampling Mode --------
            # commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            # [maxPayloadLen, commId] = commModule.open(timId, True)

            # payload = XdcrIdle(channelId).setSampleMode(samplingMode)
            # msgId = Message.getNextId()
            # commModule.writeMsg(commId, time_out, payload, True, msgId)

            # commModule.close(commId)
            # # -------------------------------------

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            [maxPayloadLen, commId] = commModule.open(timId, True)

            payload = XdcrOperate(channelId).readDataSet(0)

            msgId = Message.getNextId()
            commModule.writeMsg(commId, time_out, payload, True, msgId)

            commModule.wait_events[msgId].wait()

            [payload, last] = commModule.readRsp(commId, time_out, msgId, 4095)

            [successFlag, outArgs] = Codec.decodeResponse(payload)
            
            offset = outArgs.getByIndex(0)
   
            if(offset.value < 2**32 - 1):
                sensorData = outArgs.getByIndex(1)
                result.putByName("result", Argument(sensorData.typeCode, sensorData.value))

            commModule.close(commId)

        return result

    def writeData(self, transCommId, time_out, samplingMode, value):
        
        commSession = ts.CommSession.getCommSession(self.commSessons, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        for i in range(len(tims)):
            timId = tims[i]
            channelId = channels[i]

            # # ------- Change Sampling Mode --------
            # commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            # [maxPayloadLen, commId] = commModule.open(timId, True)

            # payload = XdcrIdle(channelId).setSampleMode(samplingMode)
            # msgId = Message.getNextId()
            # commModule.writeMsg(commId, time_out, payload, True, msgId)

            # commModule.close(commId)
            # # -------------------------------------

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            [maxPayloadLen, commId] = commModule.open(timId, False)

            payload = XdcrOperate(channelId).writeDataSet(0, value.getByIndex(i).value)

            msgId = Message.getNextId()
            commModule.writeMsg(commId, time_out, payload, True, msgId)

            commModule.close(commId)


    def startReadData(self, transCommId, triggerTime, time_out, samplingMode, callback):

        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        opId = ts.Operation.getNextId()
        operation = ts.Operation(opId, 0, callback)
        self.nb_operations.append(operation)

        for i in range(len(tims)):
            timId = tims[i]
            channelId = channels[i]

            # # ------- Change Sampling Mode --------
            # commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            # [maxPayloadLen, commId] = commModule.open(timId, True)

            # payload = XdcrIdle(channelId).setSampleMode(samplingMode)
            # msgId = Message.getNextId()
            # commModule.writeMsg(commId, time_out, payload, True, msgId)

            # commModule.close(commId)
            # # -------------------------------------

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            [maxPayloadLen, commId] = commModule.open(timId, True)

            payload = XdcrOperate(channelId).readDataSet(0)

            msgId = Message.getNextId()
            commModule.writeMsg(commId, time_out, payload, True, msgId)

            operation.msgIds.append(msgId)

            commModule.close(commId)
        
        operation.complete = True

        return opId

    def startWriteData(self, transCommId, triggerTime, time_out, samplingMode, value, callback):
        
        commSession = ts.CommSession.getCommSession(self.commSessons, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        opId = ts.Operation.getNextId()
        operation = ts.Operation(opId, 1, callback)
        self.nb_operations.append(operation)

        for i in range(len(tims)):
            timId = tims[i]
            channelId = channels[i]

            # # ------- Change Sampling Mode --------
            # commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            # [maxPayloadLen, commId] = commModule.open(timId, True)

            # payload = XdcrIdle(channelId).setSampleMode(samplingMode)
            # msgId = Message.getNextId()
            # commModule.writeMsg(commId, time_out, payload, True, msgId)

            # commModule.close(commId)
            # # -------------------------------------

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            [maxPayloadLen, commId] = commModule.open(timId, False)

            payload = XdcrOperate(channelId).writeDataSet(0, value.getByIndex(i).value)

            msgId = Message.getNextId()
            commModule.writeMsg(commId, time_out, payload, True, msgId)

            operation.msgIds.append(msgId)

            commModule.close(commId)

        operation.complete = True

        return opId

    def startStream(self, transCommId, callback):

        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        opId = ts.Operation.getNextId()
        operation = ts.Operation(opId, 2, callback)
        self.nb_operations.append(operation)

        for i in range(len(tims)):
            timId = tims[i]
            channelId = channels[i]

            # # ------- Change Sampling Mode --------
            # commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            # [maxPayloadLen, commId] = commModule.open(timId, True)

            # payload = XdcrIdle(channelId).setSampleMode(samplingMode)
            # msgId = Message.getNextId()
            # commModule.writeMsg(commId, time_out, payload, True, msgId)

            # commModule.close(commId)
            # # -------------------------------------

            commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
            [maxPayloadLen, commId] = commModule.open(timId, False)

            payload = XdcrOperate(channelId).readDataSet(0)
            payload = XdcrIdle(channelId).setXmitMode(2)

            msgId = Message.getNextId()
            commModule.writeMsg(commId, -1, payload, True, msgId)

            operation.msgIds.append(msgId)

            commModule.close(commId)
        
        operation.complete = True

        return opId


    def cancel(self, operationId):

        operation = ts.Operation.getOperationById(self.nb_operations, operationId)
        
        if(operation != None):
            self.nb_operations.remove(operation)
