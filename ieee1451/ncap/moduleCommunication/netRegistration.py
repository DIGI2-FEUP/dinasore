from unittest import TestCase
from ieee1451.ncap.teds.teds import TEDS, TEDS_ACCESS_CODES
import moduleCommunication.moduleCommunication as mc
from moduleCommunication.registration import *

class NetRegistration(Registration):
    
    def registerModule(self, commInterface, technologyId, name):

        moduleId = mc.CommModuleDotX.getNextId()
        commModule = mc.CommModuleDotX(self, commInterface, technologyId, name, moduleId)

        self.commModules.append(commModule)
        
        return moduleId
    
    def registerDestination(self, destId, moduleId):

        tim = TIM(destId)
        
        commModule = mc.CommModuleDotX.getCommModule(self.commModules, moduleId)

        commModule.addTim(tim)
        
        maxChan = 0
        
        if(destId != 0 and destId != 2):
            
            #Read META TEDS from TIM
            #print("Register TIM id = " + str(destId))
            [maxPayloadLen, commId] = commModule.open(tim.destId, True)

            payload = CommonCmd(0).readTEDS(TEDS_ACCESS_CODES.MetaTEDS.value, 0)

            msgId = mc.Message.getNextId()
            commModule.writeMsg(commId, -1, payload, True, msgId)
            
            commModule.wait_events[msgId].wait(3)
            
            if(commModule.wait_events[msgId].is_set()):

                [payload, last] = commModule.readRsp(commId, -1, msgId, 4095)
                
                [successFlag, outArgs] = Codec.decodeResponse(payload)

                offset = outArgs.getByIndex(0)
                rawTEDSBlock = outArgs.getByIndex(1)

                commModule.close(commId)

                teds = TEDS.from_bytes(rawTEDSBlock.value)
                maxChan = teds.data_block.MaxChan

                tim.setTEDS(TEDS_ACCESS_CODES.MetaTEDS, teds)

            else:
                commModule.removeTim(tim)
                return -1


            #Read GeoLoc TEDS from TIM
            #print("Register TIM id = " + str(destId))
            [maxPayloadLen, commId] = commModule.open(tim.destId, True)

            payload = CommonCmd(0).readTEDS(TEDS_ACCESS_CODES.GeoLocTEDS.value, 0)

            msgId = mc.Message.getNextId()
            commModule.writeMsg(commId, -1, payload, True, msgId)
            
            commModule.wait_events[msgId].wait(3)
            
            if(commModule.wait_events[msgId].is_set()):

                [payload, last] = commModule.readRsp(commId, -1, msgId, 4095)
                
                [successFlag, outArgs] = Codec.decodeResponse(payload)

                offset = outArgs.getByIndex(0)
                rawTEDSBlock = outArgs.getByIndex(1)

                commModule.close(commId)

                teds = TEDS.from_bytes(rawTEDSBlock.value)

                tim.setTEDS(TEDS_ACCESS_CODES.GeoLocTEDS, teds)
            else:
                commModule.removeTim(tim)
                return -1

            # Read TRANDUCER TEDS from Transducers 
            for i in range(1, maxChan+1):

                [maxPayloadLen, commId] = commModule.open(tim.destId, True)

                payload = CommonCmd(i).readTEDS(TEDS_ACCESS_CODES.ChanTEDS.value, 0)

                msgId = mc.Message.getNextId()
                commModule.writeMsg(commId, -1, payload, True, msgId)
                
                commModule.wait_events[msgId].wait(3)
                
                if(commModule.wait_events[msgId].is_set()):

                    [payload, last] = commModule.readRsp(commId, -1, msgId, 4095)
                    
                    [successFlag, outArgs] = Codec.decodeResponse(payload)

                    offset = outArgs.getByIndex(0)
                    rawTEDSBlock = outArgs.getByIndex(1)

                    commModule.close(commId)

                    teds = TEDS.from_bytes(rawTEDSBlock.value)

                    transducer = Transducer(i, "")
                    transducer.setTEDS(TEDS_ACCESS_CODES.ChanTEDS, teds)

                    tim.addTransducer(transducer)
                    
                    while(self.transducerServices.ncap.new_transducer_event.is_set() == True):
                        pass

                    self.transducerServices.ncap.new_transducer = transducer
                    self.transducerServices.ncap.new_transducer_event.set()

                else:
                    commModule.removeTim(tim)
                    return -1

        return destId

    def unRegisterDestination(self, moduleId, destId):

        commModule = mc.CommModuleDotX.getCommModule(self.commModules, moduleId)

        tim = TIM.getTim(commModule.tims, destId)

        commModule.tims.remove(tim)

    def reportDestinations(self, moduleId, maxLen, offset, destinations):

        destinations = []

        for tim in mc.CommModuleDotX.getCommModule(self.commModules, moduleId).tims:
            destinations.append(tim.destId)

        return destinations[offset:offset+maxLen]

    def reportGroups(self, moduleId, maxLen, offset):

        groups = []

        for group in mc.CommModuleDotX.getCommModule(self.commModules, moduleId).groups:
            groups.append(group.destId)

        return groups[offset:offset+maxLen]

    def reportGroupMembers(self, moduleId, groupId, maxLen, offset):
        
        members = []

        for member in TIMGroup.getGroup(mc.CommModuleDotX.getCommModule(self.commModules, moduleId).groups, groupId):
            members.append(member.destId)
        
        return members[offset:offset:maxLen]
