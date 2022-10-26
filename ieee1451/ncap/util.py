from typing import Type
from args import *
import struct
import base64


### TO-DO ###
# New typecode : ARGUMENT_ARRAY_TC

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


class Codec:

    def encodeCommand(channelId, cmdClassId, cmdFunctionId, inArgs):
        
        payload = (channelId.to_bytes(2, 'big') + 
                    cmdClassId.to_bytes(1, 'big') + 
                    cmdFunctionId.to_bytes(1, 'big')
                    )
        
        argPayload = Codec.argumentArray2OctetArray(inArgs)
        length = len(argPayload)

        if(length > 0):
            payload = (payload + 
                    length.to_bytes(2, 'big') +
                    argPayload)

        return payload

    def decodeCommand(payload):
        
        channelId = int.from_bytes(payload[:2], 'big')
        cmdClassId = int.from_bytes(payload[2:3], 'big')
        cmdFunctionId = int.from_bytes(payload[3:4], 'big')
        
        if(cmdClassId == 128 and cmdFunctionId == 1):
            inArgs = ArgumentArray()
            inArgs.putByIndex(0, Argument(TypeCode.UINT8_TC, int.from_bytes(payload[4:5], 'big')))
        else:
            inArgs = Codec.octetArray2ArgumentArray(payload[6:])
        
        return [channelId, cmdClassId, cmdFunctionId, inArgs]
        
    def encodeResponse(successFlag, outArgs):

        payload = struct.pack('?', successFlag)

        argPayload = Codec.argumentArray2OctetArray(outArgs)

        payload = (payload + 
                    len(argPayload).to_bytes(2, 'big') + 
                    argPayload)

        return payload
    
    def encodeRegisterResponse(successFlag, random, address):

        payload = struct.pack('?', successFlag)

        payload = (payload + 
                    random.to_bytes(1, 'big') + 
                    address.to_bytes(1, 'big'))

        return payload
        
    def decodeResponse(payload):
        
        successFlag = struct.unpack('?', payload[:1])

        outArgs = Codec.octetArray2ArgumentArray(payload[3:])
        
        return [successFlag, outArgs]

    def argumentArray2OctetArray(inArgs):
        
        payload = bytes()

        for arg in inArgs.arguments:
            
            payload = payload + arg[1].typeCode.value.to_bytes(1, 'big')

            if(arg[1].typeCode == TypeCode.UINT8_TC 
                or arg[1].typeCode == TypeCode.UINT16_TC
                or arg[1].typeCode == TypeCode.UINT32_TC
                or arg[1].typeCode == TypeCode.FLOAT32_TC
                or arg[1].typeCode == TypeCode.FLOAT64_TC
                or arg[1].typeCode == TypeCode.OCTET_TC
                or arg[1].typeCode == TypeCode.BOOLEAN_TC):

                size = TypeCode.length(arg[1].typeCode)
                payload = payload + size.to_bytes(2, 'big')
                payload = payload + arg[1].value.to_bytes(size, 'big')
            
            elif(arg[1].typeCode == TypeCode.STRING_TC):
                
                size = len(arg[1].value)
                payload = payload + size.to_bytes(2, 'big')
                payload = payload + arg[1].value.encode('UTF-8')

            elif(arg[1].typeCode == TypeCode.TIME_INSTANCE_TC
                or arg[1].typeCode == TypeCode.TIME_DURATION_TC):

                size = TypeCode.length(arg[1].typeCode)
                payload = payload + size.to_bytes(2, 'big')
                payload = payload + arg[1].value.secs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                payload = payload + arg[1].value.nsecs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')

            elif(arg[1].typeCode == TypeCode.QOS_PARAMS_TC):

                size = TypeCode.length(arg[1].typeCode)
                payload = payload + size.to_bytes(2, 'big')
                payload = payload + arg[1].value.service.to_bytes(TypeCode.length(TypeCode.BOOLEAN_TC), 'big')
                payload = payload + arg[1].value.period.secs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                payload = payload + arg[1].value.period.nsecs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                payload = payload + arg[1].value.transmitSize.to_bytes(TypeCode.length(TypeCode.UINT16_TC), 'big')
                payload = payload + arg[1].value.replySize.to_bytes(TypeCode.length(TypeCode.UINT16_TC), 'big')
                payload = payload + arg[1].value.accessLatency.secs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                payload = payload + arg[1].value.accessLatency.nsecs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                payload = payload + arg[1].value.transmitLatency.secs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                payload = payload + arg[1].value.transmitLatency.nsecs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')

            elif(arg[1].typeCode == TypeCode.UINT8_ARRAY_TC
                or arg[1].typeCode == TypeCode.UINT16_ARRAY_TC
                or arg[1].typeCode == TypeCode.UINT32_ARRAY_TC
                or arg[1].typeCode == TypeCode.FLOAT32_ARRAY_TC
                or arg[1].typeCode == TypeCode.FLOAT64_ARRAY_TC
                or arg[1].typeCode == TypeCode.OCTET_ARRAY_TC
                or arg[1].typeCode == TypeCode.BOOLEAN_ARRAY_TC):
                
                size = TypeCode.length(arg[1].typeCode) * len(arg[1].value)
                payload = payload + size.to_bytes(2, 'big')

                for element in arg[1].value:
                    payload = payload + element.to_bytes(size, 'big')
                
            elif(arg[1].typeCode == TypeCode.STRING_ARRAY_TC):

                size = 0

                str_payload = bytes()

                for element in arg[1].value:
                    size = size + len(element)
                    str_payload = str_payload + len(element).to_bytes(2, 'big')
                    str_payload = str_payload + element.encode('UTF-8')
            
                payload = payload + size.to_bytes(2, 'big')
                payload = payload + str_payload

            elif(arg[1].typeCode == TypeCode.TIME_INSTANCE_ARRAY_TC
                or arg[1].typeCode == TypeCode.TIME_DURATION_ARRAY_TC):
                
                size = TypeCode.length(arg[1].typeCode) * len(arg[1].value)
                payload = payload + size.to_bytes(2, 'big')

                for element in arg[1].value:
                    payload = payload + element.secs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')
                    payload = payload + element.nsecs.to_bytes(TypeCode.length(TypeCode.UINT32_TC), 'big')

        return payload

    def octetArray2ArgumentArray(payload):
        
        outArgs = ArgumentArray()

        length = len(payload)
        index = 0
        argCount = 0

        while(length > 0):

            typeCode = TypeCode.getTypeCode(int.from_bytes(payload[index:index+1], 'big'))
            index+=1
            size = int.from_bytes(payload[index:index+2], 'big')
            index+=2

            if(typeCode == TypeCode.UINT8_TC 
                or typeCode == TypeCode.UINT16_TC
                or typeCode == TypeCode.UINT32_TC):
                
                value = int.from_bytes(payload[index:index+size], 'big')
                index+=size
            
            elif(typeCode == TypeCode.FLOAT32_TC
                or typeCode == TypeCode.FLOAT64_TC):

                value = struct.unpack('f', payload[index:index+size])
                index+=size
            
            elif(typeCode == TypeCode.OCTET_TC):

                value = payload[index:index+size]
                index+=size
            
            elif(typeCode == TypeCode.BOOLEAN_TC):

                value = struct.unpack('?', payload[index:index+size])
                index+=size
            
            elif(typeCode == TypeCode.STRING_TC):

                value = payload[index:index+size].decode("UTF-8")
                index+=size
            
            elif(typeCode == TypeCode.TIME_INSTANCE_TC):

                secs = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                nsecs = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                value = TimeInstance(secs, nsecs)
                index+=size

            elif(typeCode == TypeCode.TIME_DURATION_TC):

                secs = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                nsecs = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                value = TimeDuration(secs, nsecs)
                index+=size
            
            elif(typeCode == TypeCode.QOS_PARAMS_TC):
                
                service = struct.unpack('?', payload[index:index+1])
                index+=TypeCode.length(TypeCode.BOOLEAN_TC)
                secs1 = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                nsecs1 = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                period = TimeDuration(secs1, nsecs1)
                index+=TypeCode.length(TypeCode.TIME_DURATION_TC)
                transmitSize = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT16_TC)])
                index+=TypeCode.length(TypeCode.UINT16_TC)
                replySize = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT16_TC)])
                index+=TypeCode.length(TypeCode.UINT16_TC)
                secs2 = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                nsecs2 = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                accessLatency = TimeDuration(secs2, nsecs2)
                index+=TypeCode.length(TypeCode.TIME_DURATION_TC)
                secs3 = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                nsecs3 = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                transmitLatency = TimeDuration(secs3, nsecs3)
                index+=TypeCode.length(TypeCode.TIME_DURATION_TC)

                value = QoSParams(service, period, transmitSize, replySize, accessLatency, transmitLatency)

            elif(typeCode == TypeCode.UINT8_ARRAY_TC
                or typeCode == TypeCode.UINT16_ARRAY_TC
                or typeCode == TypeCode.UINT32_ARRAY_TC):

                size_n = TypeCode.length(typeCode)
                n = int(size / size_n)

                value = []

                for i in range(n):
                    element = int.from_bytes(payload[index:index+size_n], 'big')
                    index+=size_n
                    value.append(element)
                
            elif(typeCode == TypeCode.FLOAT32_ARRAY_TC
                or typeCode == TypeCode.FLOAT64_ARRAY_TC):

                size_n = TypeCode.length(typeCode)
                n = int(size / size_n)

                value = []

                for i in range(n):
                    element = struct.unpack('f', payload[index:index+size_n])
                    index+=size_n
                    value.append(element)
            
            elif(typeCode == TypeCode.OCTET_ARRAY_TC):

                size_n = TypeCode.length(typeCode)
                
                n = int(size / size_n)

                value = bytearray()

                for i in range(n):
                    element = payload[index:index+size_n]
                    index+=size_n
                    value = value + element
            
            elif(typeCode == TypeCode.BOOLEAN_ARRAY_TC):

                size_n = TypeCode.length(typeCode)
                n = int(size / size_n)

                value = []

                for i in range(n):
                    element = struct.unpack('?', payload[index:index+size_n])
                    index+=size_n
                    value.append(element)

            elif(typeCode == TypeCode.STRING_ARRAY_TC):
                
                lengthArray = size
                value = []

                while(lengthArray > 0):
                    length_n = int.from_bytes(payload[index:index+1], 'big')
                    index+=2
                    element = payload[index:index+length_n].decode("UTF-8")
                    value.append(element)
                    lengthArray = lengthArray - length_n
                
            elif(typeCode == TypeCode.TIME_INSTANCE_ARRAY_TC):

                size_n = TypeCode.length(typeCode)
                n = int(size / size_n)

                value = []

                for i in range(n):
                    secs = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                    nsecs = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                    element = TimeInstance(secs, nsecs)
                    index+=size_n
                    value.append(element)
            
            elif(typeCode == TypeCode.TIME_DURATION_ARRAY_TC):

                size_n = TypeCode.length(typeCode)
                n = int(size / size_n)

                value = []                

                for i in range(n):
                    secs = int.from_bytes(payload[index:index+TypeCode.length(TypeCode.UINT32_TC)])
                    nsecs = int.from_bytes(payload[index+TypeCode.length(TypeCode.UINT32_TC):index+2*TypeCode.length(TypeCode.UINT32_TC)])
                    element = TimeDuration(secs, nsecs)
                    index+=size
                    value.append(element)

            arg = Argument(typeCode, value) 
            outArgs.putByIndex(argCount, arg)

            argCount = argCount + 1
            length = length - size - 3
            
        return outArgs

    
    def argumentArray2Json(inArgs):
        
        argArrayDict = Codec.argumentArray2Dict(inArgs)

        return json.dumps(argArrayDict)


    def argumentArray2Dict(inArgs):
        
        argArray = []

        for arg in inArgs.arguments:
            
            dict = {"name": arg[0], "typeCode": arg[1].typeCode.value}

            if(arg[1].typeCode == TypeCode.UINT8_TC 
                or arg[1].typeCode == TypeCode.UINT16_TC
                or arg[1].typeCode == TypeCode.UINT32_TC
                or arg[1].typeCode == TypeCode.FLOAT32_TC
                or arg[1].typeCode == TypeCode.FLOAT64_TC
                or arg[1].typeCode == TypeCode.BOOLEAN_TC
                or arg[1].typeCode == TypeCode.STRING_TC
                or arg[1].typeCode == TypeCode.UINT8_ARRAY_TC
                or arg[1].typeCode == TypeCode.UINT16_ARRAY_TC
                or arg[1].typeCode == TypeCode.UINT32_ARRAY_TC
                or arg[1].typeCode == TypeCode.FLOAT32_ARRAY_TC
                or arg[1].typeCode == TypeCode.FLOAT64_ARRAY_TC
                or arg[1].typeCode == TypeCode.BOOLEAN_ARRAY_TC
                or arg[1].typeCode == TypeCode.STRING_ARRAY_TC):
            
                dict["value"] = arg[1].value

            elif(arg[1].typeCode == TypeCode.OCTET_TC
                or arg[1].typeCode == TypeCode.OCTET_ARRAY_TC):

                dict["value"] = base64.standard_b64encode(arg[1].value).decode()

            elif(arg[1].typeCode == TypeCode.TIME_INSTANCE_TC
                or arg[1].typeCode == TypeCode.TIME_DURATION_TC):

                pass            

            elif(arg[1].typeCode == TypeCode.QOS_PARAMS_TC):

                pass

            elif(arg[1].typeCode == TypeCode.TIME_INSTANCE_ARRAY_TC
                or arg[1].typeCode == TypeCode.TIME_DURATION_ARRAY_TC):
                
                pass

            elif(arg[1].typeCode == TypeCode.ARGUMENT_ARRAY_TC):
                dict["value"] = Codec.argumentArray2Dict(arg[1].value)

            argArray.append(dict)

        argArrayDict = {"argumentArray": argArray}

        return argArrayDict


    def json2ArgumentArray(js):

        argArrayList = json.loads(js)['argumentArray']
        argArray = Codec.dict2ArgumentArray(argArrayList)

        return argArray


    def dict2ArgumentArray(argArrayList):

        argArray = ArgumentArray()

        for argDict in argArrayList:
            
            typeCode = TypeCode.getTypeCode(argDict['typeCode'])

            if(typeCode == TypeCode.UINT8_TC 
                or typeCode == TypeCode.UINT16_TC
                or typeCode == TypeCode.UINT32_TC
                or typeCode == TypeCode.FLOAT32_TC
                or typeCode == TypeCode.FLOAT64_TC
                or typeCode == TypeCode.BOOLEAN_TC
                or typeCode == TypeCode.STRING_TC
                or typeCode == TypeCode.UINT8_ARRAY_TC
                or typeCode == TypeCode.UINT16_ARRAY_TC
                or typeCode == TypeCode.UINT32_ARRAY_TC
                or typeCode == TypeCode.FLOAT32_ARRAY_TC
                or typeCode == TypeCode.FLOAT64_ARRAY_TC
                or typeCode == TypeCode.BOOLEAN_ARRAY_TC
                or typeCode == TypeCode.STRING_ARRAY_TC):

                value = argDict["value"]

            elif(typeCode == TypeCode.OCTET_TC
                or typeCode == TypeCode.OCTET_ARRAY_TC):

                value = base64.standard_b64decode(argDict["value"].encode())
                
            elif(typeCode == TypeCode.TIME_INSTANCE_TC
                or typeCode == TypeCode.TIME_DURATION_TC):

                pass            

            elif(typeCode == TypeCode.QOS_PARAMS_TC):

                pass

            elif(typeCode == TypeCode.TIME_INSTANCE_ARRAY_TC
                or typeCode == TypeCode.TIME_DURATION_ARRAY_TC):
                
                pass
            
            elif(typeCode == TypeCode.ARGUMENT_ARRAY_TC):

                value = Codec.dict2ArgumentArray(argDict["value"])

            arg = Argument(typeCode, value)
            argArray.putByName(argDict['name'], arg)

        return argArray


class CodecManagement:

    def register(self, moduleId, customCode):
        pass

    def unregister(self, moduleId):
        pass


if (__name__ == '__main__'):

    argumentArray = []
    argumentArray.append(['', Argument(1,2)])
    argumentArray.append(['', Argument(2,2)])
    argumentArray.append(['', Argument(1,2)])
    argumentArray.append(['', Argument(3,2)])
    
    payload = Codec.argumentArray2OctetArray(argumentArray)

    print(payload)
    print(len(payload))

    payload2 = Codec.encodeCommand(1, 2, 3, argumentArray)
    print(payload2)