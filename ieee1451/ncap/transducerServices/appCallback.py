class AppCallback:

    def measurementUpdate(self, operationId, measValues, status):
        pass

    def actuationComplete(self, operationId, status):
        pass

    def statusChange(self, operationId, status):
        pass

    def commandComplete(self, operationId, status):
        pass

    def triggerComplete(self, operationId, status):
        pass
