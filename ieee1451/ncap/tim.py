import threading


class TIM:

    nextId = 2

    def __init__(self, destId):
        self.destId = destId

        self.address = destId           
        
        self.transducers = []
        self.teds = {}

    def getNextId():

        TIM.nextId = TIM.nextId + 1
        
        return TIM.nextId - 1

    def setNextId(nextId):

        TIM.nextId = nextId
        
    def addTransducer(self, transducer):
        transducer.tim = self
        print("- New Transducer: TIM_ID = " + str(self.destId) + " / TRANSDUCER_ID = " + str(transducer.id))
        self.transducers.append(transducer)

    def getTim(tims, timId):
        
        if(tims == []):
            return None

        for x in tims:
            if(x.destId == timId):
                return x

        return None
    

    def getTransducer(self, id):
        
        for x in self.transducers:
            if(x.id == id):
                return x
        
        return None
    
    def getTransducers(self):
        return self.transducers

    def getTEDS(self, accessCode):
        if accessCode in self.teds:
            return self.teds[accessCode]
        else:
            return None

    def setTEDS(self, acessCode, teds):
        self.teds[acessCode] = teds


class TIMGroup:

    nextId = 1

    def __init__(self, destId):
        self.destId = destId

        self.timIds = []

    def getNextId():

        TIMGroup.nextId = TIMGroup.nextId + 1
        
        return TIMGroup.nextId - 1
    
    def getGroup(groups, groupId):

        if(groups == []):
            return None

        for x in groups:
            if(x.destId == groupId):
                return x
        
        return None
    
    def hasTim(self, timId):
        
        result = False

        for id in self.timIds:
            if(timId == id):
                result = True
        
        return result

    

class Transducer:

    def __init__(self, id, name):

        self.id = id
        self.name = name
        self.teds = {}

        self.tim = None

    def getTEDS(self, accessCode):
        if accessCode in self.teds:
            return self.teds[accessCode]
        else:
            return None

    def setTEDS(self, acessCode, teds):
        self.teds[acessCode] = teds
