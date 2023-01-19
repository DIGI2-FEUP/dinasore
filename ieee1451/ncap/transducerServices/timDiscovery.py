from moduleCommunication.moduleCommunication import *
from teds.teds import TEDS_ACCESS_CODES

class TimDiscovery:

    def reportCommModule(self):

        moduleIds = []

        for module in self.commModuleDot0.commModules:
            moduleIds.append(module.id)

        return moduleIds

    def reportTims(self, moduleId):

        timIds = [] 

        commModule = CommModuleDotX.getCommModule(self.commModuleDot0.commModules, moduleId)

        if(commModule != None):
            for tim in commModule.tims:
                if (tim.destId != 0 and tim.destId != 2):
                    timIds.append(tim.destId)

        return timIds

    def reportChannels(self, timId):

        channelIds = []
        names = []

        for commModule in self.commModuleDot0.commModules:

            tim = TIM.getTim(commModule.tims, timId)

            if (tim != None):
                break

        if (tim == None):
            return [[],[]]

        for x in tim.getTransducers():
            channelIds.append(x.id)
            names.append(x.name)
        
        return channelIds, names

    def getTimIdByUUID(self, tim_uuid):
        
        tim_id = None

        for commModule in self.commModuleDot0.commModules:
            for tim in commModule.tims:
                if(tim.destId > 2):

                    meta_teds = tim.getTEDS(TEDS_ACCESS_CODES.MetaTEDS).data_block
                    uuid = meta_teds.UUID

                    if(uuid == tim_uuid):
                        tim_id = tim.destId
                        break
            
            if(tim_id != None):
                break
    
        return tim_id