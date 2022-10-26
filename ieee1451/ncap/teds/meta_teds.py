from args import *
import teds.teds as teds
import struct

class Meta_TEDS_Data_Block:

    def __init__(self, UUID, OholdOff, SHoldOff, TestTime, MaxChan):
        
        self.TEDSID = teds.TEDS_Identifier_Structure(teds.TEDS_ACCESS_CODES.MetaTEDS)
        self.UUID = UUID

        self.OholdOff = OholdOff
        self.SHoldOff = SHoldOff
        self.TestTime = TestTime
        
        self.MaxChan = MaxChan

    def to_bytes(self):

        tvlTEDSID = teds.TEDS_TLV_Block(3, 4, self.TEDSID.to_bytes())
        tvlUUID = teds.TEDS_TLV_Block(4, 10, self.UUID)
        tvlOholfOff = teds.TEDS_TLV_Block(10, 4, struct.pack('>f', self.OholdOff))
        if(self.SHoldOff != None):
            tvlSholdOff = teds.TEDS_TLV_Block(11, 4, struct.pack('>f', self.SHoldOff))
        tvlTestTime = teds.TEDS_TLV_Block(12, 4, struct.pack('>f', self.TestTime))
        tvlMaxChan = teds.TEDS_TLV_Block(13, 2, self.MaxChan.to_bytes(2, 'big'))

        barray = bytearray()

        barray.extend(tvlTEDSID.to_bytes(1))
        barray.extend(tvlUUID.to_bytes(self.TEDSID.tuple_length))
        barray.extend(tvlOholfOff.to_bytes(self.TEDSID.tuple_length))
        if(self.SHoldOff != None):
            barray.extend(tvlSholdOff.to_bytes(self.TEDSID.tuple_length))
        barray.extend(tvlTestTime.to_bytes(self.TEDSID.tuple_length))
        barray.extend(tvlMaxChan.to_bytes(self.TEDSID.tuple_length))

        return barray

    def to_argumentArray(self):

        argArray = ArgumentArray()

        argArray.putByName('TEDSID', Argument(TypeCode.UINT32_TC, int.from_bytes(self.TEDSID.to_bytes(), 'big')))
        argArray.putByName('UUID', Argument(TypeCode.OCTET_ARRAY_TC, self.UUID))
        argArray.putByName('OholdOff', Argument(TypeCode.FLOAT32_TC, self.OholdOff))
        if(self.SHoldOff != None):
            argArray.putByName('SholdOff', Argument(TypeCode.FLOAT32_TC, self.SHoldOff))
        argArray.putByName('TestTime', Argument(TypeCode.FLOAT32_TC, self.TestTime))
        argArray.putByName('MaxChan', Argument(TypeCode.UINT16_TC, self.MaxChan))

        return argArray

    def from_bytes(barray):

        tLength = 1
        size = len(barray)
        index = 0
        
        [uuid, oholdoff, sholdoff, testTime, maxChan] = [None, None, None, None, None]

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length
            if(tvl.type == 3):
                tvlTEDSID = tvl
                tLength = int.from_bytes(tvlTEDSID.value[3:4], 'big')
            if(tvl.type == 4):
                uuid = tvl.value
            if(tvl.type == 10):
                oholdoff = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 11):
                sholdoff = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 12):
                testTime = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 13):
                maxChan = int.from_bytes(tvl.value, 'big')
    
        metaTEDS = Meta_TEDS_Data_Block(uuid, oholdoff, sholdoff, testTime, maxChan)

        return metaTEDS

    def from_argumentArray(argArray):

        uuid = argArray.getByName('UUID').value
        oholdoff = argArray.getByName('OholdOff').value
        sholdoff = None
        if(argArray.getByName('SholdOff') != None):
            sholdoff = argArray.getByName('SholdOff').value
        testTime = argArray.getByName('TestTime').value
        maxChan = argArray.getByName('MaxChan').value

        metaTEDS = Meta_TEDS_Data_Block(uuid, oholdoff, sholdoff, testTime, maxChan)

        return metaTEDS