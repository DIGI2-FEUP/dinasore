from args import *
import teds.teds as teds
import xml.etree.ElementTree as ET

class GeoLoc_TEDS_Data_Block:

    def __init__(self):
        
        self.TEDSID = teds.TEDS_Identifier_Structure(teds.TEDS_ACCESS_CODES.GeoLocTEDS)
        
        self.DirBlock = None

        self.SubSum = None
        
        self.XMLText = None
        self.XMLSum = None

    def to_bytes(self):

        tvlTEDSID = teds.TEDS_TLV_Block(3, 4, self.TEDSID.to_bytes())
        
        tvlDirBlock = self.DirBlock.to_TVL(11, self.TEDSID.tuple_length)
        tvlSubSum = teds.TEDS_TLV_Block(12, 2, self.SubSum.to_bytes(2, 'big'))
        tvlXMLText = teds.TEDS_TLV_Block(128, self.DirBlock.Length - 2, bytes(self.XMLText, 'ascii'))
        tvlXMLSum = teds.TEDS_TLV_Block(129, 2, self.XMLSum.to_bytes(2, 'big'))

        barray = bytearray()
        barray.extend(tvlTEDSID.to_bytes(1))
        barray.extend(tvlDirBlock.to_bytes(self.TEDSID.tuple_length))
        barray.extend(tvlSubSum.to_bytes(self.TEDSID.tuple_length))
        barray.extend(tvlXMLText.to_bytes(self.TEDSID.tuple_length))
        barray.extend(tvlXMLSum.to_bytes(self.TEDSID.tuple_length))

        return barray

    def to_argumentArray(self):

        argArray = ArgumentArray()

        argArray.putByName('TEDSID', Argument(TypeCode.UINT32_TC, int.from_bytes(self.TEDSID.to_bytes(), 'big')))
        argArray.putByName('DirBlock', Argument(TypeCode.ARGUMENT_ARRAY_TC, self.DirBlock.to_argumentArray()))
        argArray.putByName('SubSum', Argument(TypeCode.UINT16_TC, self.SubSum))
        argArray.putByName('XMLText', Argument(TypeCode.STRING_TC, self.XMLText))
        argArray.putByName('XMLSum', Argument(TypeCode.UINT16_TC, self.XMLSum))

        return argArray

    def from_bytes(barray):

        tLength = 1
        size = len(barray)
        index = 0
        
        geoLocTEDS = GeoLoc_TEDS_Data_Block()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 3):
                tLength = int.from_bytes(tvl.value[3:4], 'big')
            if(tvl.type == 11):
                geoLocTEDS.DirBlock = DirBlock.from_bytes(tvl.value, tLength)
            if(tvl.type == 12):
                geoLocTEDS.SubSum = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 128):
                geoLocTEDS.XMLText = tvl.value.decode("ascii")
            if(tvl.type == 129):
                geoLocTEDS.XMLSum = int.from_bytes(tvl.value, 'big')
    
        return geoLocTEDS

    def from_argumentArray(argArray):
        
        geoLocTEDS = GeoLoc_TEDS_Data_Block()

        if(argArray.getByName('DirBlock') != None):
            geoLocTEDS.DirBlock = DirBlock.from_argumentArray(argArray.getByName('DirBlock').value)
        if(argArray.getByName('SubSum') != None):
            geoLocTEDS.SubSum = argArray.getByName('SubSum').value
        if(argArray.getByName('XMLText') != None):
            geoLocTEDS.XMLText = argArray.getByName('XMLText').value
        if(argArray.getByName('XMLSum') != None):
            geoLocTEDS.XMLSum = argArray.getByName('XMLSum').value

        return geoLocTEDS


class DirBlock:

    def __init__(self):
        self.LangCode = None
        self.Offset = None
        self.Length = None

    def to_TVL(self, type, tuple_length):

        barray = bytearray()
       
        tvlLangCode = teds.TEDS_TLV_Block(20, 2, self.LangCode.to_bytes(2, 'big'))
        tvlOffset = teds.TEDS_TLV_Block(21, 4, self.Offset.to_bytes(4, 'big'))
        tvlLength = teds.TEDS_TLV_Block(22, 4, self.Length.to_bytes(4, 'big'))

        barray.extend(tvlLangCode.to_bytes(tuple_length))
        barray.extend(tvlOffset.to_bytes(tuple_length))
        barray.extend(tvlLength.to_bytes(tuple_length))

        return teds.TEDS_TLV_Block(type, len(barray), barray)

    def to_argumentArray(self):

        argArray = ArgumentArray()

        argArray.putByName('LangCode', Argument(TypeCode.UINT16_TC, self.LangCode))
        argArray.putByName('Offset', Argument(TypeCode.UINT32_TC, self.Offset))
        argArray.putByName('Length', Argument(TypeCode.UINT32_TC, self.Length))

        return argArray
    
    def from_bytes(barray, tLength):

        size = len(barray)
        index = 0
        
        dirBlock = DirBlock()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 20):
                dirBlock.LangCode = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 21):
                dirBlock.Offset = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 22):
                dirBlock.Length = int.from_bytes(tvl.value, 'big')
            
        return dirBlock

    def from_argumentArray(argArray):

        dirBlock = DirBlock()

        if(argArray.getByName('LangCode') != None):
            dirBlock.Repeats = argArray.getByName('LangCode').value
        if(argArray.getByName('Offset') != None):
            dirBlock.SOrigin = argArray.getByName('Offset').value
        if(argArray.getByName('Length') != None):
            dirBlock.StepSize = argArray.getByName('Length').value
        
        return dirBlock


class GeoLoc_Util:
    
    def xmlText2PosXY(xmlText):
        root = ET.fromstring(xmlText)

        pos = root.find('{http://www.opengis.net/gml}pos')
        
        words = pos.text.split(' ')

        return [float(words[0]), float(words[1])]
