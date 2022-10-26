from pprint import PrettyPrinter
from util import *

class Command:

    cmdClasses = {
        1 : 'CommonCmd',
        2 : 'XdcrIdle',
        3 : 'XdcrOperate',
        4 : 'XdcrEither',
        5 : 'TIMsleep',
        6 : 'TIMActive',
        7 : 'AnyState',
        
        128: 'DotX_DIGI2'
    }

    def __init__(self, destination, cmdClass):
        self.destination = destination
        self.cmdClass = cmdClass
        self.cmdFunction = None
        self.cmdArguments = ArgumentArray()

    def getMessage(self):

        return Codec.encodeCommand(self.destination, self.cmdClass, self.cmdFunction, self.cmdArguments)

    def getResponse(cmdArguments):

        return Codec.encodeResponse(True, cmdArguments)

    def getRegisterResponse(random, address):

        return Codec.encodeRegisterResponse(True, random, address)

# Commands common to the TIM and TransducerChannel
class CommonCmd(Command):

    cmdFunctions = {
        1 : 'Query TEDS', 
        2 : 'Read TEDS segment',
        3 : 'Write TEDS segment',
        4 : 'Update TEDS',
        5 : 'Run self-test',
        6 : 'Write service request mask',
        7 : 'Read service request mask',
        8 : 'Read status-event register',
        9 : 'Read status-condition register',
        10 : 'Clear status-event register',
        11 : 'Write status-event protocol state',
        12 : 'Read status-event protocol state'
    }

    def __init__(self, destination):
        super().__init__(destination, 1)

    def queryTEDS(self, accessCode):
        self.cmdFunction = 1
        self.cmdArguments.putByName('TEDSAccessCode', Argument(TypeCode.UINT8_TC, accessCode))
        return self.getMessage()
    
    def readTEDS(self, accessCode, offset):
        self.cmdFunction = 2
        self.cmdArguments.putByName('TEDSAccessCode', Argument(TypeCode.UINT8_TC, accessCode))
        self.cmdArguments.putByName('TEDSOffset', Argument(TypeCode.UINT32_TC, offset))
        return self.getMessage()
    
    def writeTEDS(self, accessCode, offset, rawBlock):
        self.cmdFunction = 3
        self.cmdArguments.putByName('TEDSAccessCode', Argument(TypeCode.UINT8_TC, accessCode))
        self.cmdArguments.putByName('TEDSOffset', Argument(TypeCode.UINT32_TC, offset))
        self.cmdArguments.putByName('RawTEDSBlock', Argument(TypeCode.OCTET_ARRAY_TC, rawBlock))
        return self.getMessage()

    def updateTEDS(self, accessCode):
        self.cmdFunction = 4
        self.cmdArguments.putByName('TEDSAccessCode', Argument(TypeCode.UINT8_TC, accessCode))
        return self.getMessage()
    
    def runTest(self, test2Run):
        self.cmdFunction = 5
        self.cmdArguments.putByName('Test2Run', Argument(TypeCode.UINT8_TC, test2Run))
        return self.getMessage()
    
    def writeSRMask(self, SRMask):
        self.cmdFunction = 6
        self.cmdArguments.putByName('SRMask', Argument(TypeCode.UINT32_TC, SRMask))
        return self.getMessage()
    
    def readSRMask(self):
        self.cmdFunction = 7
        return self.getMessage()
    
    def readSERegister(self):
        self.cmdFunction = 8
        return self.getMessage()

    def readSCRegister(self):
        self.cmdFunction = 9
        return self.getMessage()
    
    def clearSERegister(self):
        self.cmdFunction = 10
        return self.getMessage()

    def writeSEProtocol(self, SEProtocol):
        self.cmdFunction = 11
        self.cmdArguments.putByName('SEProtocol', Argument(TypeCode.BOOLEAN_TC, SEProtocol))
        return self.getMessage()
    
    def readSEProtocol(self):
        self.cmdFunction = 12
        return self.getMessage()


# Transducer idle state
class XdcrIdle(Command):

    cmdFunctions = {
        1 : 'Set TransducerChannel data repetition count', 
        2 : 'Set TransducerChannel pre-trigger count',
        3 : 'AddressGroup definition',
        4 : 'Sampling mode',
        5 : 'Data Transmission mode',
        6 : 'Buffered state',
        7 : 'End-of-data-set operation',
        8 : 'Actuator-halt mode',
        9 : 'Edge-to-report',
        10 : 'Calibrate TransducerChannel',
        11 : 'Zero TransducerChannel',
        12 : 'Write corrections state',
        13 : 'Read corrections state',
        14 : 'Write TransducerChannel initiate trigger state',
        15 : 'Write TransducerChannel initiate trigger configuration'
    }
    
    def __init__(self, destination):
        super().__init__(destination, 2)

    def setTCRepCount(self, repCount):
        self.cmdFunction = 1
        self.cmdArguments.putByName('RepCount', Argument(TypeCode.UINT16_TC, repCount))
        return self.getMessage()

    def setTCPreTrigCount(self, preTrigCount):
        self.cmdFunction = 2
        self.cmdArguments.putByName('PreTrigCount', Argument(TypeCode.UINT16_TC, preTrigCount))
        return self.getMessage()
    
    def setAddGroup(self, groupAdd):
        self.cmdFunction = 3
        self.cmdArguments.putByName('GroupAdd', Argument(TypeCode.UINT16_TC, groupAdd))
        return self.getMessage()
    
    def setSampleMode(self, sampleMode):
        self.cmdFunction = 4
        self.cmdArguments.putByName('SampleMode', Argument(TypeCode.UINT8_TC, sampleMode))
        return self.getMessage()

    def setXmitMode(self, xmitMode):
        self.cmdFunction = 5
        self.cmdArguments.putByName('XmitMode', Argument(TypeCode.UINT8_TC, xmitMode))
        return self.getMessage()
    
    def setBuffState(self, buffState):
        self.cmdFunction = 6
        self.cmdArguments.putByName('BufferOnOff', Argument(TypeCode.BOOLEAN_TC, buffState))
        return self.getMessage()
    
    def setEDSMode(self, EDSMode):
        self.cmdFunction = 7
        self.cmdArguments.putByName('EndDataSetMode', Argument(TypeCode.UINT8_TC, EDSMode))
        return self.getMessage()
    
    def setActHaltMode(self, actHaltMode):
        self.cmdFunction = 8
        self.cmdArguments.putByName('ActuatorHalt', Argument(TypeCode.UINT8_TC, actHaltMode))
        return self.getMessage()
    
    def setEdgeReport(self, edgeReport):
        self.cmdFunction = 9
        self.cmdArguments.putByName('EdgeReported', Argument(TypeCode.UINT8_TC, edgeReport))
        return self.getMessage()
    
    def calibrate(self):
        self.cmdFunction = 10
        return self.getMessage()
    
    def zeroTC(self):
        self.cmdFunction = 11
        return self.getMessage()

    def writeCorrectState(self, correctState):
        self.cmdFunction = 12
        self.cmdArguments.putByName('CorrectState', Argument(TypeCode.UINT8_TC, correctState))
        return self.getMessage()
    
    def readCorrectState(self):
        self.cmdFunction = 13
        return self.getMessage()
    
    def writeInitTrigState(self, trigState):
        self.cmdFunction = 14
        self.cmdArguments.putByName('EventTrig', Argument(TypeCode.BOOLEAN_TC, trigState))
        return self.getMessage()
    
    def writeInitTrigConfig(self, destID, channelID, qosParams):
        self.cmdFunction = 15
        self.cmdArguments.putByName('InitTrig.destId', Argument(TypeCode.UINT16_TC, destID))
        self.cmdArguments.putByName('InitTrig.channelId', Argument(TypeCode.UINT16_TC, channelID))
        self.cmdArguments.putByName('InitTrig.qosParams', Argument(TypeCode.QOS_PARAMS_TC, qosParams))
        return self.getMessage()
    

# Transducer operating state
class XdcrOperate(Command):

    cmdFunctions = {
        1 : 'Read TransducerChannel data-set segment', 
        2 : 'Write TransducerChannel data set segment',
        3 : 'Trigger command',
        4 : 'Abort Trigger'
    }

    def __init__(self, destination):
        super().__init__(destination, 3)

    def readDataSet(self, offset):
        self.cmdFunction = 1
        self.cmdArguments.putByName('DataSetOffset', Argument(TypeCode.UINT32_TC, offset))
        return self.getMessage()

    def writeDataSet(self, offset, dataBlock):
        self.cmdFunction = 2
        self.cmdArguments.putByName('WriteActuator.Offset', Argument(TypeCode.UINT32_TC, offset))
        self.cmdArguments.putByName('WriteActuator.DataBlock', Argument(TypeCode.OCTET_ARRAY_TC, dataBlock))
        return self.getMessage()

    def trigger(self):
        self.cmdFunction = 3
        return self.getMessage()
    
    def abortTrigger(self):
        self.cmdFunction = 4
        return self.getMessage()


# Transducer either idle or operating state
class XdcrEither(Command):

    cmdFunctions = {
        1 : 'TransducerChannel Operate', 
        2 : 'TransducerChannel Idle',
        3 : 'Write TransducerChannel trigger state',
        4 : 'Read TransducerChannel trigger state',
        5 : 'Read TransducerChannel data repetition count',
        6 : 'Read TransducerChannel pre-trigger count',
        7 : 'Read AddressGroup assignment',
        8 : 'Read Sampling mode',
        9 : 'Read data transmission mode',
        10 : 'Read buffered state',
        11 : 'Read end-of-data-set operation',
        12 : 'Read actuator halt mode',
        13 : 'Read edge-to-report mode',
        14 : 'Read TransducerChannel initiate trigger state',
        15 : 'Read TransducerChannel initiate trigger configuration',
        16 : 'Device clear'
    }

    def __init__(self, destination):
        super().__init__(destination, 4)

    def operate(self):
        self.cmdFunction = 1
        self.getMessage()
    
    def idle(self):
        self.cmdFunction = 2
        return self.getMessage()
    
    def writeTrigState(self, trigState):
        self.cmdFunction = 3
        self.cmdArguments.putByName('TrigState', Argument(TypeCode.BOOLEAN_TC, trigState))
        return self.getMessage()

    def readTrigState(self):
        self.cmdFunction = 4
        return self.getMessage()
    
    def readTCRepCount(self):
        self.cmdFunction = 5
        return self.getMessage()
 
    def readTCPreTrigCount(self):
        self.cmdFunction = 6
        return self.getMessage()

    def readAddrGroup(self):
        self.cmdFunction = 7
        return self.getMessage()
    
    def readSampleMode(self):
        self.cmdFunction = 8
        return self.getMessage()
    
    def readXmitMode(self):
        self.cmdFunction = 9
        return self.getMessage()
    
    def readBuffState(self):
        self.cmdFunction = 10
        return self.getMessage()
    
    def readEDSMode(self):
        self.cmdFunction = 11
        return self.getMessage()
    
    def readActHaltMode(self):
        self.cmdFunction = 12
        return self.getMessage()

    def readEdgeReport(self):
        self.cmdFunction = 13
        return self.getMessage()
    
    def readInitTrigState(self):
        self.cmdFunction = 14
        return self.getMessage()
    
    def readInitTrigConfig(self):
        self.cmdFunction = 15
        return self.getMessage()
    
    def clear(self):
        self.cmdFunction = 16
        return self.getMessage()


# Sleep state
class TIMsleep(Command):

    cmdFunctions = {
        1 : 'Wake-up'
    }    

    def __init__(self, destination):
        super().__init__(destination, 5)
   
    def wakeUp(self):
        self.cmdFunction = 1
        return self.getMessage()


# Tim active state commands
class TIMActive(Command):

    cmdFunctions = {
        1 : 'Read TIM version', 
        2 : 'TIM Sleep',
        3 : 'Store operational setup',
        4 : 'Recall operational setup',
        5 : 'Read IEEE 1451.0 Version'
    }

    def __init__(self, destination):
        super().__init__(destination, 6)

    def readTIMVersion(self):
        self.cmdFunction = 1
        return self.getMessage()
    
    def sleep(self):
        self.cmdFunction = 2
        return self.getMessage()
    
    def storeState(self, state):
        self.cmdFunction = 3
        self.cmdArguments.putByName('StorState', Argument(TypeCode.UINT8_TC, state))
        return self.getMessage()
    
    def recallState(self, state):
        self.cmdFunction = 4
        self.cmdArguments.putByName('StorState', Argument(TypeCode.UINT8_TC, state))
        return self.getMessage()

    def readIEEE14510Version(self):
        self.cmdFunction = 5
        return self.getMessage()


# Any state
class AnyState(Command):

    cmdFunctions = {
        1 : 'Reset'
    }

    def __init__(self, destination):
        super().__init__(destination, 7)

    def reset(self):
        self.cmdFunction = 1
        return self.getMessage()

class DotX_DIGI2(Command):

    cmdFunctions = {
        1 : 'Register',
        2 : 'Discovery'
    }

    def __init__(self, destination):
        super().__init__(destination, 128)
    
    def register(self, random):
        self.cmdFunction = 1
        self.cmdArguments.putByName('Random', Argument(TypeCode.UINT8_TC, random))
        return self.getMessage()

    def register_response(random, address):
        return Command.getRegisterResponse(random, address)
    
    def discover(self):
        self.cmdFunction = 2
        return self.getMessage()