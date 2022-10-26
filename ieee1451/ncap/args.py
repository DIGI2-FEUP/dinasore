import json
from enum import Enum

class ArgumentArray:

    def __init__(self):

        self.arguments = []  # [ ['name, Argument], ['name', Argument] ]
    
    def getByName(self, name):
        
        for arg in self.arguments:
            if(arg[0] == name):
                return arg[1]
        
        return None

    def getByIndex(self, index):
        
        if(len(self.arguments) > index):
            return self.arguments[index][1]
        else:
            return None

    def putByName(self, name, value):

        self.arguments.append([name, value])

    def putByIndex(self, index, value):

        for i in range(index - len(self.arguments) + 1):
            self.arguments.append(None)
        
        self.arguments.insert(index, [None, value])

    def stringToIndex(self, name):

        # pesquisar no vetor ou hardcoded com definição dos argumentos dos comandos?
        pass

    def getNames(self):
        pass

    def getIndexes(self):
        pass

    def size(self):
        
        return len(self.arguments)

class Argument:

    def __init__(self, typeCode, value):
        
        self.typeCode = typeCode
        self.value = value


class TypeCode(Enum):
    UNKNOWN_TC = 0

    UINT8_TC = 1
    UINT16_TC = 2
    UINT32_TC = 3
    FLOAT32_TC = 4
    FLOAT64_TC = 5
    STRING_TC = 6
    OCTET_TC = 7
    BOOLEAN_TC = 8
    TIME_INSTANCE_TC = 9
    TIME_DURATION_TC = 10
    QOS_PARAMS_TC = 11

    UINT8_ARRAY_TC = 12
    UINT16_ARRAY_TC = 13
    UINT32_ARRAY_TC = 14
    FLOAT32_ARRAY_TC = 15
    FLOAT64_ARRAY_TC = 16
    STRING_ARRAY_TC = 17
    OCTET_ARRAY_TC = 18
    BOOLEAN_ARRAY_TC = 19
    TIME_INSTANCE_ARRAY_TC = 20
    TIME_DURATION_ARRAY_TC = 21

    ARGUMENT_ARRAY_TC = 25

    def getTypeCode(value):
        if(value == 0):
            return TypeCode.UNKNOWN_TC
        elif(value == 1):
            return TypeCode.UINT8_TC
        elif(value == 2):
            return TypeCode.UINT16_TC
        elif(value == 3):
            return TypeCode.UINT32_TC
        elif(value == 4):
            return TypeCode.FLOAT32_TC
        elif(value == 5):
            return TypeCode.FLOAT64_TC
        elif(value == 6):
            return TypeCode.STRING_TC
        elif(value == 7):
            return TypeCode.OCTET_TC
        elif(value == 8):
            return TypeCode.BOOLEAN_TC
        elif(value == 9):
            return TypeCode.TIME_INSTANCE_TC
        elif(value == 10):
            return TypeCode.TIME_DURATION_TC
        elif(value == 11):
            return TypeCode.QOS_PARAMS_TC
        elif(value == 12):
            return TypeCode.UINT8_TC
        elif(value == 13):
            return TypeCode.UINT8_TC
        elif(value == 14):
            return TypeCode.UINT8_TC
        elif(value == 15):
            return TypeCode.UINT8_TC
        elif(value == 16):
            return TypeCode.UINT8_TC
        elif(value == 17):
            return TypeCode.UINT8_TC
        elif(value == 18):
            return TypeCode.OCTET_ARRAY_TC
        elif(value == 19):
            return TypeCode.UINT8_TC
        elif(value == 20):
            return TypeCode.UINT8_TC
        elif(value == 21):
            return TypeCode.UINT8_TC
        elif(value == 25):
            return TypeCode.ARGUMENT_ARRAY_TC
        

    def length(typecode):
        if(typecode == TypeCode.UNKNOWN_TC):
            return -1
        elif(typecode == TypeCode.UINT8_TC):
            return 1
        elif(typecode == TypeCode.UINT16_TC):
            return 2
        elif(typecode == TypeCode.UINT32_TC):
            return 4
        elif(typecode == TypeCode.FLOAT32_TC):
            return 4
        elif(typecode == TypeCode.FLOAT64_TC):
            return 8
        elif(typecode == TypeCode.STRING_TC):
            return None
        elif(typecode == TypeCode.OCTET_TC):
            return 1
        elif(typecode == TypeCode.BOOLEAN_TC):
            return 1
        elif(typecode == TypeCode.TIME_INSTANCE_TC):
            return 8
        elif(typecode == TypeCode.TIME_DURATION_TC):
            return 8
        elif(typecode == TypeCode.QOS_PARAMS_TC):
            return 29
        elif(typecode == TypeCode.UINT8_ARRAY_TC):
            return TypeCode.length(TypeCode.UINT8_TC)
        elif(typecode == TypeCode.UINT16_ARRAY_TC):
            return TypeCode.length(TypeCode.UINT16_TC)
        elif(typecode == TypeCode.UINT32_ARRAY_TC):
            return TypeCode.length(TypeCode.UINT32_TC)
        elif(typecode == TypeCode.FLOAT32_ARRAY_TC):
            return TypeCode.length(TypeCode.FLOAT32_TC)
        elif(typecode == TypeCode.FLOAT64_ARRAY_TC):
            return TypeCode.length(TypeCode.FLOAT64_TC)
        elif(typecode == TypeCode.STRING_ARRAY_TC):
            return None
        elif(typecode == TypeCode.OCTET_ARRAY_TC):
            return TypeCode.length(TypeCode.OCTET_TC)
        elif(typecode == TypeCode.BOOLEAN_ARRAY_TC):
            return TypeCode.length(TypeCode.BOOLEAN_TC)
        elif(typecode == TypeCode.TIME_INSTANCE_ARRAY_TC):
            return TypeCode.length(TypeCode.TIME_INSTANCE_TC)
        elif(typecode == TypeCode.TIME_DURATION_ARRAY_TC):
            return TypeCode.length(TypeCode.TIME_DURATION_TC)
        elif(typecode == TypeCode.ARGUMENT_ARRAY_TC):
            return None

class QoSParams:
    
    def __init__(self, service, period, transmitSize, replySize, accessLatency, transmitLatency):
        self.service = service
        self.period = period
        self.transmitSize = transmitSize
        self.replySize = replySize
        self.accessLatency = accessLatency
        self.transmitLatency = transmitLatency

class TimeRepresentation:

    def __init__(self, secs, nsecs):
        self.secs = secs
        self.nsecs = nsecs

class TimeDuration:

    def __init__(self, secs, nsecs):
        self.secs = secs
        self.nsecs = nsecs

class TimeInstance:

    def __init__(self, secs, nsecs):
        self.secs = secs
        self.nsecs = nsecs


class ErrorCode(Enum):

    NO_ERROR = 0