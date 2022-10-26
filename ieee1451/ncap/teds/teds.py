import enum
from teds.teds_utils import *
from teds.meta_teds import *
from teds.chan_teds import *
from teds.geo_teds import *

from numpy import float32, uint16, uint8

class TEDS:

    def __init__(self, data_block):
        self.length = calc_length(data_block) + 2
        self.data_block = data_block
        self.checksum = calc_checksum(data_block)

    def to_argumentArray(self):
        
        argArray = self.data_block.to_argumentArray()

        argArray.putByName('length', Argument(TypeCode.UINT32_TC, self.length))
        argArray.putByName('checksum', Argument(TypeCode.UINT16_TC, self.checksum))

        return argArray

    def to_bytes(self):

        barray = (len(self.data_block.to_bytes())  + 2).to_bytes(4, 'big')
        barray = barray + self.data_block.to_bytes()
        barray = barray + self.checksum.to_bytes(2, 'big')

        return barray
    
    def from_argumentArray(argArray):
        
        tedsType = argArray.getByName('TEDSID').value.to_bytes(4, 'big')[1]
        accessCode = TEDS_ACCESS_CODES.getAccessCode(tedsType)

        argArray.arguments.remove(['length', argArray.getByName('length')])
        argArray.arguments.remove(['checksum', argArray.getByName('checksum')])
        
        tedsDataBlock = TEDS.dataBlock_fromArgumentArray(accessCode, argArray)

        return TEDS(tedsDataBlock)

    def from_bytes(rawTEDSBlock):

        tedsType = rawTEDSBlock[7]
        accessCode = TEDS_ACCESS_CODES.getAccessCode(tedsType)

        size = len(rawTEDSBlock)
        tedsDataBlock = TEDS.dataBlock_fromBytes(accessCode, rawTEDSBlock[4:size-2])

        return TEDS(tedsDataBlock)

    def dataBlock_fromBytes(accessCode, rawTEDSBlock):
        if(accessCode == TEDS_ACCESS_CODES.MetaTEDS):
            tedsDataBlock = Meta_TEDS_Data_Block.from_bytes(rawTEDSBlock)
        elif(accessCode == TEDS_ACCESS_CODES.ChanTEDS):
            tedsDataBlock = Transducer_Channel_TEDS_Data_Block.from_bytes(rawTEDSBlock)
        elif(accessCode == TEDS_ACCESS_CODES.GeoLocTEDS):
            tedsDataBlock = GeoLoc_TEDS_Data_Block.from_bytes(rawTEDSBlock)
        return tedsDataBlock

    def dataBlock_fromArgumentArray(accessCode, argArray):
        if(accessCode == TEDS_ACCESS_CODES.MetaTEDS):
            tedsDataBlock = Meta_TEDS_Data_Block.from_argumentArray(argArray)
        elif(accessCode == TEDS_ACCESS_CODES.ChanTEDS):
            tedsDataBlock = Transducer_Channel_TEDS_Data_Block.from_argumentArray(argArray)        
        elif(accessCode == TEDS_ACCESS_CODES.GeoLocTEDS):
            tedsDataBlock = GeoLoc_TEDS_Data_Block.from_argumentArray(argArray)  
        return tedsDataBlock

class TEDS_TLV_Block():

    def __init__(self, type, length, value):

        self.type = type
        self.length = length
        self.value = value

    def to_bytes(self, tLength):
        barray = self.type.to_bytes(1, 'big') + self.length.to_bytes(tLength, 'big') + self.value
        return barray

    def from_bytes(barray, tLength):
        type = int.from_bytes(barray[0:1], 'big')
        length = int.from_bytes(barray[1:1+tLength], 'big')
        value = barray[1+tLength:1+tLength+length]
        return TEDS_TLV_Block(type, length, value)


class TEDS_Identifier_Structure():

    def __init__(self, teds_class):
        #TEDSID field type = 3
        self.type = 0x03
        #Fixed length of 4 bytess
        self.length = 0x04
        #TEDS IEEE 1451.0 family
        self.family = 0x00
        #This field identifies the TEDS being accessed.
        self.teds_class = uint8(teds_class)
        #Original version
        self.version = 0x01
        #TO-DO
        self.tuple_length = 0x01

    def get_tlv(self):
        return TEDS_TLV_Block(self.type, self.get_value(), self.length)

    def to_bytes(self):
        return bytes([self.family, self.teds_class, self.version, self.tuple_length])

    def get_value(self):
        return [self.family, self.teds_class, self.version, self.tuple_length]


class TEDS_ACCESS_CODES(enum.IntEnum):

    MetaTEDS = 0x01          # required
    MetaIdTEDS = 0x02           # optional
    ChanTEDS = 0x03          # required
    ChanIdTEDS = 0x04           # optional
    CalTEDS = 0x05              # optional
    CalIdTEDS = 0x06            # optional
    EUASTEDS = 0x07             # optional
    FreqRespTEDS = 0x08         # optional
    TransferTEDS = 0x09         # optional
    CommandTEDS = 0x0A          # optional
    TitleTEDS = 0x0B            # optional
    XdcrName = 0x0C          # required
    PHYTEDS = 0x0D           # required
    GeoLocTEDS = 0x0E           # optional
    UnitsExtention = 0x0F       # optional

    def getAccessCode(value):
        if(value == 1):
            return TEDS_ACCESS_CODES.MetaTEDS
        elif(value == 2):
            return TEDS_ACCESS_CODES.MetaIdTEDS
        elif(value == 3):
            return TEDS_ACCESS_CODES.ChanTEDS
        elif(value == 4):
            return TEDS_ACCESS_CODES.ChanIdTEDS
        elif(value == 5):
            return TEDS_ACCESS_CODES.CalTEDS
        elif(value == 6):
            return TEDS_ACCESS_CODES.CalIdTEDS
        elif(value == 7):
            return TEDS_ACCESS_CODES.EUASTEDS
        elif(value == 8):
            return TEDS_ACCESS_CODES.FreqRespTEDS
        elif(value == 9):
            return TEDS_ACCESS_CODES.TransferTEDS
        elif(value == 10):
            return TEDS_ACCESS_CODES.CommandTEDS
        elif(value == 11):
            return TEDS_ACCESS_CODES.TitleTEDS
        elif(value == 12):
            return TEDS_ACCESS_CODES.XdcrName
        elif(value == 13):
            return TEDS_ACCESS_CODES.PHYTEDS
        elif(value == 14):
            return TEDS_ACCESS_CODES.GeoLocTEDS
        elif(value == 15):
            return TEDS_ACCESS_CODES.UnitsExtention