class CommManager:

    def getCommModule(self, moduleId):
        
        commObject = None
        type = None
        technologyId = None

        for module in self.commModuleDot0.commModules:
            if(moduleId == module.id):
                commObject = module
                type = module.interfaceType
                technologyId = module.technologyId

        return [commObject, type, technologyId]