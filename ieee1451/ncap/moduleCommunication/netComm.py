from moduleCommunication.comm import *

import moduleCommunication.moduleCommunication as mc

class NetComm(Comm):

    def open(self, destId, twoWay):

        commId = mc.CommChannel.getNextId()

        self.commChannels.append(mc.CommChannel(self, commId, destId, twoWay))

        return [mc.CommChannel.maxPayloadLen, commId]

    def openQoS(self, destId, twoWay, maxPayloadLn, commId, qosParams):
        pass

    def close(self, commId):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        commChannel.close()

        self.commChannels.remove(commChannel)

    def readMsg(self, commId, time_out, length):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        message = commChannel.inMessages[0]
      
        payload = message.readMessage(length)

        if(message.index == len(message.payload)):
            last = True   
        else:
            last = False

        return [length, payload, last]

    def readRsp(self, commId, time_out, msgId, maxLen):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        message = mc.Message.getMessage(commChannel.inMessages, msgId)
        if(message != None):
            commChannel.inMessages.remove(message)
            payload = message.readMessage(maxLen)
            
            if(message.index == len(message.payload)):
                last = True   
            else:
                last = False

            return [payload, last]
        else:
            return [None, None]

    def writeMsg(self, commId, time_out, payload, last, msgId):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        message = mc.Message.getMessage(commChannel.outMessages, msgId)

        if(message == None):
            message = mc.Message(msgId, payload)
            commChannel.outMessages.append(message)
        else:
            message.payload = message.payload + payload

        if(last == True):
            commChannel.sendMessage(message)

    def writeRsp(self, commId, time_out, payload, last):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        msgId = commChannel.inMessages[0].msgId

        message = mc.Message.getMessage(commChannel.outMessages, msgId)

        if(message == None):
            message = mc.Message(msgId, payload)
            commChannel.outMessages.append(message)
        else:
            message.payload = message.payload + payload

        if(last == True):
            commChannel.sendMessage(message)

    def flush(self, commId):
        pass

    def readSize(self, commId, cacheSize):
        pass

    def setPayloadSize(self, commId, size):
        pass
    
    def abort(self, commId):
        pass

    def commStatus(self, commId, msgId):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        message = mc.Message.getMessage(commChannel.outMessages, msgId)

        return message.status

    def discoverDestinations(self):
        
        print("Starting TIM Discovery")

        timeout = 5

        [maxPayloadLen, commId] = self.open(0, True)

        payload = DotX_DIGI2(0).discover()

        msgId = mc.Message.getNextId()
        self.writeMsg(commId, timeout, payload, True, msgId)

        start_time = time.time_ns()
        self.wait_events[msgId].wait(timeout)

        while(time.time_ns() - start_time < timeout * 1000000000):

            if(self.wait_events[msgId].is_set()):
                
                [payload, last] = self.readRsp(commId, timeout, msgId, 4095)
                # Deal with last
                if(payload != None):
                    [successFlag, outArgs] = Codec.decodeResponse(payload)

                    address = outArgs.getByIndex(0)

                    nextId = TIM.nextId
                    TIM.setNextId(address.value)
                    destId = TIM.getNextId()
                    
                    self.commModuleDot0.registerDestination(destId, self.id)

                    if(nextId > address.value):
                        TIM.setNextId(nextId)

                    #print("Register TIM id = " + str(address.value))

        self.wait_events.pop(msgId)

        self.close(commId)

        print("Finish TIM Discovery")

    def joinGroup(self, groupId, destId):
        
        group = TIMGroup.getGroup(self.groups, groupId)

        if(group == None):
            group = TIMGroup(groupId)
            self.groups.append(group)

        if(group.hasTim(destId) == False):
            group.timIds.append(destId)

    def leaveGroup(self, groupId, destId):
        
        group = TIMGroup.getGroup(self.groups, groupId)

        group.timIds.remove(destId)

    def lookupDestId(self, commId, destId):

        commChannel = mc.CommChannel.getCommChannel(self.commChannels, commId)

        return commChannel.destId

    def setRemoteConfiguration(self, commId, time_out, params):
        pass

    def getRemoteConfiguration(self, commId, time_out, params):
        pass

    def sendRemoteCommand(self, commId, time_out, cmdClassId, cmdFunctionId, inArgs):
        pass

