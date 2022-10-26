from moduleCommunication.moduleCommunication import *

class Registration:

    def unRegisterModule(self, moduleId):
        
        commModule = CommModuleDotX.getCommModule(self.commModules, moduleId)

        self.commModules.remove(commModule)

    def reportModules(self, maxLen, offset):

        moduleIds = []

        for module in self.commModules:
            moduleIds.append(module.id)

        return moduleIds[offset:offset+maxLen]

    def getCommModule(self, moduleId, commObject, type, technologyId):
        
        commObject = CommModuleDotX.getCommModule(self.commModules, moduleId)
        type = commObject.interfaceType
        technologyId = commObject.technologyId

        return [commObject, type, technologyId]
