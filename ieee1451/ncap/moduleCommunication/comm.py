from moduleCommunication.moduleCommunication import *

class Comm:

    def init(self):
        pass

    def shutdown(self):
        pass

    def sleep(self, duration):
        pass

    def wakeup(self):
        pass

    def setLocalConfiguration(self, params):
        pass

    def getLocalConfiguration(self, params):
        pass

    def sendLocalCommand(self, cmdClassId, cmdFunctionId, inArgs):
        pass
        
    def describe(self):

        return [self.interfaceType, self.technologyId, self.name]