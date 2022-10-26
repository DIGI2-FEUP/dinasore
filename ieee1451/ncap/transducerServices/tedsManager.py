from teds.teds import *
from moduleCommunication.moduleCommunication import *

import transducerServices.transducerServices as ts

class TedsManager:

    def readTeds(self, transCommId, timeout, tedsType):
        
        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        if(len(tims) > 1):
            return None
        
        timId = tims[0]
        channelId = channels[0]

        commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
        tim = TIM.getTim(commModule.tims, timId)

        if(channelId == 0):
            TEDS = tim.getTEDS(TEDS_ACCESS_CODES.getAccessCode(tedsType))
        else:
            channel = tim.getTransducer(channelId)
            TEDS = channel.getTEDS(TEDS_ACCESS_CODES.getAccessCode(tedsType))

        if(TEDS == None):
            return None
            
        tedsArgArray = TEDS.to_argumentArray()

        return tedsArgArray


    def writeTeds(self, transCommId, timeout, tedsType, argArrayTeds):
        
        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        if(len(tims) > 1):
            return None

        accessCode = TEDS_ACCESS_CODES.getAccessCode(tedsType)
        teds = TEDS.from_argumentArray(argArrayTeds)

        rawBlock = teds.to_bytes()

        timId = tims[0]
        channelId = channels[0]
        
        commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
        [maxPayloadLen, commId] = commModule.open(timId, False)

        payload = CommonCmd(channelId).writeTEDS(tedsType, 0, rawBlock)
        msgId = Message.getNextId()
        #commModule.writeMsg(commId, timeout, payload, True, msgId)

        commModule.close(commId)

        tim = TIM.getTim(commModule.tims, timId)
        print(timId)

        if(channelId == 0):
            tim.setTEDS(accessCode, teds)
        else:
            channel = TIM.getTransducer(channelId)
            channel.setTEDS(accessCode, teds)


    def readRawTeds(self, transCommId, timeout, tedsType):
        
        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        if(len(tims) > 1):
            return None

        tim = tims[0]
        channel = channels[0]   

        commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, tim)
        [maxPayloadLen, commId] = commModule.open(tim, True)

        payload = CommonCmd(channel).readTEDS(tedsType, 0)

        msgId = Message.getNextId()
        commModule.writeMsg(commId, timeout, payload, True, msgId)
        
        commModule.wait_events[msgId].wait()
        
        [payload, last] = commModule.readRsp(commId, timeout, msgId, 4095)
        # Deal with last
        
        [successFlag, outArgs] = Codec.decodeResponse(payload)

        offset = outArgs.getByIndex(0)
        rawTEDSBlock = outArgs.getByIndex(1)

        commModule.close(commId)
        
        return rawTEDSBlock.value


    def writeRawTeds(self, transCommId, timeout, tedsType, rawTeds):
        
        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        if(len(tims) > 1):
            return None

        timId = tims[0]
        channelId = channels[0]
        
        commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
        [maxPayloadLen, commId] = commModule.open(timId, False)

        payload = CommonCmd(channelId).writeTEDS(tedsType, 0, rawTeds)

        msgId = Message.getNextId()
        commModule.writeMsg(commId, timeout, payload, True, msgId)

        commModule.close(commId)


    def updateTedsCache(self, transCommId, timeout, tedsType):
        
        commSession = ts.CommSession.getCommSession(self.commSessions, transCommId)

        tims = commSession.tims
        channels = commSession.channels

        if(len(tims) > 1):
            return None

        timId = tims[0]
        channelId = channels[0]   

        commModule = CommModuleDotX.getCommModuleByTim(self.commModuleDot0.commModules, timId)
        [maxPayloadLen, commId] = commModule.open(timId, True)

        payload = CommonCmd(channelId).readTEDS(tedsType, 0)

        msgId = Message.getNextId()
        commModule.writeMsg(commId, timeout, payload, True, msgId)
        
        commModule.wait_events[msgId].wait()
        
        [payload, last] = commModule.readRsp(commId, timeout, msgId, response[3])
        # Deal with last
        
        [successFlag, outArgs] = Codec.decodeResponse(payload)

        offset = outArgs.getByIndex(0)
        rawTEDSBlock = outArgs.getByIndex(1)

        commModule.close(commId)
        
        accessCode = TEDS_ACCESS_CODES.getAccessCode(tedsType)
        teds = TEDS.from_bytes(rawTEDSBlock.value)

        tim = TIM.getTim(commModule.tims, timId)

        if(channelId == 0):
            tim.setTEDS(accessCode, teds)
        else:
            channel = TIM.getTransducer(channelId)
            channel.setTEDS(accessCode, teds)