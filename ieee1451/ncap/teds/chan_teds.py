from args import *
import teds.teds as teds
import struct

class Transducer_Channel_TEDS_Data_Block:

    def __init__(self):
        
        self.TEDSID = teds.TEDS_Identifier_Structure(teds.TEDS_ACCESS_CODES.ChanTEDS)

        self.CalKey = None
        self.ChanType = None

        self.PhyUnits = None

        self.LowLimit = None
        self.HiLimit = None
        self.OError = None
        self.SelfTest = None
        self.MRange = None

        self.Sample = None
        
        self.DataSet = None

        self.UpdateT = None
        self.WSetupT = None
        self.RSetupT = None
        self.SPeriod = None
        self.WarmUpT = None
        self.RDelayT = None
        self.TestTime = None

        self.TimeSrc = None
        self.InPropDl = None
        self.OutPropD = None
        self.TSError = None

        self.Sampling = None

        self.DataXmit = None
        self.Buffered = None
        self.EndOfSet = None
        self.EdgeRpt = None
        self.ActHalt = None
        
        self.Direction = None
        self.DAngles = None

        self.ESOption = None

    def to_bytes(self):

        barray = bytearray()

        tvlTEDSID = teds.TEDS_TLV_Block(3, 4, self.TEDSID.to_bytes())
        barray.extend(tvlTEDSID.to_bytes(1))
        
        if(self.CalKey != None):
            tvlCalKey = teds.TEDS_TLV_Block(10, 1, self.ChanType.to_bytes(1, 'big'))
            barray.extend(tvlCalKey.to_bytes(self.TEDSID.tuple_length))
        if(self.ChanType != None):      
            tvlChanType = teds.TEDS_TLV_Block(11, 1, self.ChanType.to_bytes(1, 'big'))
            barray.extend(tvlChanType.to_bytes(self.TEDSID.tuple_length))

        if(self.PhyUnits != None):
            tvlPhyUnits = self.PhyUnits.to_TVL(12, self.TEDSID.tuple_length)
            barray.extend(tvlPhyUnits.to_bytes(self.TEDSID.tuple_length))

        if(self.LowLimit != None):      
            tvlLowLimit = teds.TEDS_TLV_Block(13, 4, struct.pack('>f', self.LowLimit))
            barray.extend(tvlLowLimit.to_bytes(self.TEDSID.tuple_length))
        if(self.HiLimit != None):      
            tvlHiLimit = teds.TEDS_TLV_Block(14, 4, struct.pack('>f', self.HiLimit))
            barray.extend(tvlHiLimit.to_bytes(self.TEDSID.tuple_length))
        if(self.OError != None):      
            tvlOError = teds.TEDS_TLV_Block(15, 4, struct.pack('>f', self.OError))
            barray.extend(tvlOError.to_bytes(self.TEDSID.tuple_length))
        if(self.SelfTest != None):      
            tvlSelfTest = teds.TEDS_TLV_Block(16, 1, self.SelfTest.to_bytes(1, 'big'))
            barray.extend(tvlSelfTest.to_bytes(self.TEDSID.tuple_length))
        if(self.MRange != None):      
            tvlMRange = teds.TEDS_TLV_Block(17, 1, self.MRange.to_bytes(1, 'big'))
            barray.extend(tvlMRange.to_bytes(self.TEDSID.tuple_length))
        
        if(self.Sample != None):
            tvlSample = self.Sample.to_TVL(18, self.TEDSID.tuple_length)
            barray.extend(tvlSample.to_bytes(self.TEDSID.tuple_length))

        if(self.DataSet != None):
            tvlDataSet = self.DataSet.to_TVL(19, self.TEDSID.tuple_length)
            barray.extend(tvlDataSet.to_bytes(self.TEDSID.tuple_length))

        if(self.UpdateT != None):      
            tvlUpdateT = teds.TEDS_TLV_Block(20, 4, struct.pack('>f', self.UpdateT))
            barray.extend(tvlUpdateT.to_bytes(self.TEDSID.tuple_length))
        if(self.WSetupT != None):      
            tvlWSetupT = teds.TEDS_TLV_Block(21, 4, struct.pack('>f', self.WSetupT))
            barray.extend(tvlWSetupT.to_bytes(self.TEDSID.tuple_length))
        if(self.RSetupT != None):      
            tvlRSetupT = teds.TEDS_TLV_Block(22, 4, struct.pack('>f', self.RSetupT))
            barray.extend(tvlRSetupT.to_bytes(self.TEDSID.tuple_length))
        if(self.SPeriod != None):      
            tvlSPeriod = teds.TEDS_TLV_Block(23, 4, struct.pack('>f', self.SPeriod))
            barray.extend(tvlSPeriod.to_bytes(self.TEDSID.tuple_length))
        if(self.WarmUpT != None):      
            tvlWarmUpT = teds.TEDS_TLV_Block(24, 4, struct.pack('>f', self.WarmUpT))
            barray.extend(tvlWarmUpT.to_bytes(self.TEDSID.tuple_length))
        if(self.RDelayT != None):      
            tvlRDelayT = teds.TEDS_TLV_Block(25, 4, struct.pack('>f', self.RDelayT))
            barray.extend(tvlRDelayT.to_bytes(self.TEDSID.tuple_length))
        if(self.TestTime != None):      
            tvlTestTime = teds.TEDS_TLV_Block(26, 4, struct.pack('>f', self.TestTime))
            barray.extend(tvlTestTime.to_bytes(self.TEDSID.tuple_length))

        if(self.TimeSrc != None):      
            tvlTimeSrc = teds.TEDS_TLV_Block(27, 1, self.TimeSrc.to_bytes(1, 'big'))
            barray.extend(tvlTimeSrc.to_bytes(self.TEDSID.tuple_length))
        if(self.InPropDl != None):      
            tvlInPropDl = teds.TEDS_TLV_Block(28, 4, struct.pack('>f', self.InPropDl))
            barray.extend(tvlInPropDl.to_bytes(self.TEDSID.tuple_length))
        if(self.OutPropD != None):      
            tvlOutPropD = teds.TEDS_TLV_Block(29, 4, struct.pack('>f', self.OutPropD))
            barray.extend(tvlOutPropD.to_bytes(self.TEDSID.tuple_length))
        if(self.TSError != None):      
            tvlTSError = teds.TEDS_TLV_Block(30, 4, struct.pack('>f', self.TSError))
            barray.extend(tvlTSError.to_bytes(self.TEDSID.tuple_length))

        if(self.Sampling != None):      
            tvlSampling = self.Sampling.to_TVL(31, self.TEDSID.tuple_length)
            barray.extend(tvlSampling.to_bytes(self.TEDSID.tuple_length))

        if(self.DataXmit != None):      
            tvlDataXmit = teds.TEDS_TLV_Block(32, 1, self.DataXmit.to_bytes(1, 'big'))
            barray.extend(tvlDataXmit.to_bytes(self.TEDSID.tuple_length))
        if(self.Buffered != None):      
            tvlBuffered = teds.TEDS_TLV_Block(33, 1, self.Buffered.to_bytes(1, 'big'))
            barray.extend(tvlBuffered.to_bytes(self.TEDSID.tuple_length))
        if(self.EndOfSet != None):      
            tvlEndOfSet = teds.TEDS_TLV_Block(34, 1, self.EndOfSet.to_bytes(1, 'big'))
            barray.extend(tvlEndOfSet.to_bytes(self.TEDSID.tuple_length))
        if(self.EdgeRpt != None):      
            tvlEdgeRpt = teds.TEDS_TLV_Block(35, 1, self.EdgeRpt.to_bytes(1, 'big'))
            barray.extend(tvlEdgeRpt.to_bytes(self.TEDSID.tuple_length))
        if(self.ActHalt != None):      
            tvlActHalt = teds.TEDS_TLV_Block(36, 1, self.ActHalt.to_bytes(1, 'big'))
            barray.extend(tvlActHalt.to_bytes(self.TEDSID.tuple_length))

        if(self.Direction != None):      
            tvlDirection = teds.TEDS_TLV_Block(37, 4, struct.pack('>f', self.Direction))
            barray.extend(tvlDirection.to_bytes(self.TEDSID.tuple_length))
        if(self.DAngles != None):      
            tvlDAngles = teds.TEDS_TLV_Block(38, 8, struct.pack('>f', self.DAngles[0]) + struct.pack('>f', self.DAngles[1]))
            barray.extend(tvlDAngles.to_bytes(self.TEDSID.tuple_length))

        if(self.ESOption != None):      
            tvlESOption = teds.TEDS_TLV_Block(39, 1, self.ESOption.to_bytes(1, 'big'))
            barray.extend(tvlESOption.to_bytes(self.TEDSID.tuple_length))
        
        return barray

    def to_argumentArray(self):
        
        argArray = ArgumentArray()
        
        argArray.putByName('TEDSID', Argument(TypeCode.UINT32_TC, int.from_bytes(self.TEDSID.to_bytes(), 'big')))
        
        if(self.CalKey != None):
            argArray.putByName('CalKey', Argument(TypeCode.UINT8_TC, self.CalKey))
        if(self.ChanType != None):      
            argArray.putByName('ChanType', Argument(TypeCode.UINT8_TC, self.ChanType))

        if(self.PhyUnits != None):
            argArray.putByName('PhyUnits', Argument(TypeCode.ARGUMENT_ARRAY_TC, self.PhyUnits.to_argumentArray()))

        if(self.LowLimit != None):      
            argArray.putByName('LowLimit', Argument(TypeCode.UINT16_TC, self.LowLimit))
        if(self.HiLimit != None):      
            argArray.putByName('HiLimit', Argument(TypeCode.FLOAT32_TC, self.HiLimit))
        if(self.OError != None):      
            argArray.putByName('OError', Argument(TypeCode.FLOAT32_TC, self.OError))
        if(self.SelfTest != None):      
            argArray.putByName('SelfTest', Argument(TypeCode.UINT8_TC, self.SelfTest))            
        if(self.MRange != None):      
            argArray.putByName('MRange', Argument(TypeCode.UINT8_TC, self.MRange))            
        
        if(self.Sample != None):
            argArray.putByName('Sample', Argument(TypeCode.ARGUMENT_ARRAY_TC, self.Sample.to_argumentArray()))
        
        if(self.DataSet != None):
            argArray.putByName('DataSet', Argument(TypeCode.ARGUMENT_ARRAY_TC, self.DataSet.to_argumentArray()))

        if(self.UpdateT != None):      
            argArray.putByName('UpdateT', Argument(TypeCode.FLOAT32_TC, self.UpdateT))            
        if(self.WSetupT != None):      
            argArray.putByName('WSetupT', Argument(TypeCode.FLOAT32_TC, self.WSetupT))            
        if(self.RSetupT != None):      
            argArray.putByName('RSetupT', Argument(TypeCode.FLOAT32_TC, self.RSetupT))            
        if(self.SPeriod != None):      
            argArray.putByName('SPeriod', Argument(TypeCode.FLOAT32_TC, self.SPeriod))            
        if(self.WarmUpT != None):      
            argArray.putByName('WarmUpT', Argument(TypeCode.FLOAT32_TC, self.WarmUpT))            
        if(self.RDelayT != None):      
            argArray.putByName('RDelayT', Argument(TypeCode.FLOAT32_TC, self.RDelayT))            
        if(self.TestTime != None):      
            argArray.putByName('TestTime', Argument(TypeCode.FLOAT32_TC, self.TestTime))            

        if(self.TimeSrc != None):      
            argArray.putByName('TimeSrc', Argument(TypeCode.UINT8_TC, self.TimeSrc))            
        if(self.InPropDl != None):      
            argArray.putByName('InPropDl', Argument(TypeCode.FLOAT32_TC, self.InPropDl))            
        if(self.OutPropD != None):      
            argArray.putByName('OutPropD', Argument(TypeCode.FLOAT32_TC, self.OutPropD))            
        if(self.TSError != None):      
            argArray.putByName('TSError', Argument(TypeCode.FLOAT32_TC, self.TSError))            

        if(self.Sampling != None):      
            argArray.putByName('Sampling', Argument(TypeCode.ARGUMENT_ARRAY_TC, self.Sampling.to_argumentArray()))

        if(self.DataXmit != None):      
            argArray.putByName('DataXmit', Argument(TypeCode.UINT8_TC, self.DataXmit))            
        if(self.Buffered != None):      
            argArray.putByName('Buffered', Argument(TypeCode.UINT8_TC, self.Buffered))            
        if(self.EndOfSet != None):      
            argArray.putByName('EndOfSet', Argument(TypeCode.UINT8_TC, self.EndOfSet))            
        if(self.EdgeRpt != None):      
            argArray.putByName('EdgeRpt', Argument(TypeCode.UINT8_TC, self.EdgeRpt))            
        if(self.ActHalt != None):      
            argArray.putByName('ActHalt', Argument(TypeCode.UINT8_TC, self.ActHalt))            

        if(self.Direction != None):      
            argArray.putByName('Direction', Argument(TypeCode.FLOAT32_TC, self.Direction))            
        if(self.DAngles != None):      
            argArray.putByName('DAngles', Argument(TypeCode.FLOAT32_ARRAY_TC, self.DAngles))            

        if(self.ESOption != None):      
            argArray.putByName('ESOption', Argument(TypeCode.UINT8_TC, self.ESOption))            

        return argArray

    def from_bytes(barray):

        tLength = 1
        size = len(barray)
        index = 0
        
        chanTEDS = Transducer_Channel_TEDS_Data_Block()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 3):
                tLength = int.from_bytes(tvl.value[3:4], 'big')
            if(tvl.type == 10):
                chanTEDS.CalKey = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 11):
                chanTEDS.ChanType = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 12):
                chanTEDS.PhyUnits = PhyUnits.from_bytes(tvl.value, tLength)
            if(tvl.type == 13):
                chanTEDS.LowLimit = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 14):
                chanTEDS.HiLimit = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 15):
                chanTEDS.OError = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 16):
                chanTEDS.SelfTest = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 17):
                chanTEDS.MRange = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 18):
                chanTEDS.Sample = Sample.from_bytes(tvl.value, tLength)
            if(tvl.type == 19):
                chanTEDS.DataSet = DataSet.from_bytes(tvl.value, tLength)
            if(tvl.type == 20):
                chanTEDS.UpdateT = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 21):
                chanTEDS.WSetupT = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 22):
                chanTEDS.RSetupT = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 23):
                chanTEDS.SPeriod = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 24):
                chanTEDS.WarmUpT = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 25):
                chanTEDS.RDelayT = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 26):
                chanTEDS.TestTime = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 27):
                chanTEDS.TimeSrc = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 28):
                chanTEDS.InPropDl = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 29):
                chanTEDS.OutPropD = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 30):
                chanTEDS.TSError = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 31):
                chanTEDS.Sampling = Sampling.from_bytes(tvl.value, tLength)
            if(tvl.type == 32):
                chanTEDS.DataXmit = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 33):
                chanTEDS.Buffered = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 34):
                chanTEDS.EndOfSet = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 35):
                chanTEDS.EdgeRpt = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 36):
                chanTEDS.ActHalt = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 37):
                chanTEDS.Direction = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 38):
                chanTEDS.DAngles = [struct.unpack('>f', tvl.value[:4])[0], struct.unpack('>f', tvl.value[4:])[0]]
            if(tvl.type == 39):
                chanTEDS.ESOption = int.from_bytes(tvl.value, 'big')    

        return chanTEDS

    def from_argumentArray(argArray):
        
        chanTEDS = Transducer_Channel_TEDS_Data_Block()

        if(argArray.getByName('CalKey') != None):
            chanTEDS.CalKey = argArray.getByName('CalKey').value
        if(argArray.getByName('ChanType') != None):
            chanTEDS.ChanType = argArray.getByName('ChanType').value
        if(argArray.getByName('PhyUnits') != None):
            chanTEDS.PhyUnits = PhyUnits.from_argumentArray(argArray.getByName('PhyUnits').value)
        if(argArray.getByName('LowLimit') != None):
            chanTEDS.LowLimit = argArray.getByName('LowLimit').value
        if(argArray.getByName('HiLimit') != None):
            chanTEDS.HiLimit = argArray.getByName('HiLimit').value
        if(argArray.getByName('OError') != None):
            chanTEDS.OError = argArray.getByName('OError').value
        if(argArray.getByName('SelfTest') != None):
            chanTEDS.SelfTest = argArray.getByName('SelfTest').value
        if(argArray.getByName('MRange') != None):
            chanTEDS.MRange = argArray.getByName('MRange').value
        if(argArray.getByName('Sample') != None):
            chanTEDS.Sample = Sample.from_argumentArray(argArray.getByName('Sample').value)
        if(argArray.getByName('DataSet') != None):
            chanTEDS.DataSet = DataSet.from_argumentArray(argArray.getByName('DataSet').value)
        if(argArray.getByName('UpdateT') != None):
            chanTEDS.UpdateT = argArray.getByName('UpdateT').value
        if(argArray.getByName('WSetupT') != None):
            chanTEDS.WSetupT = argArray.getByName('WSetupT').value
        if(argArray.getByName('RSetupT') != None):
            chanTEDS.RSetupT = argArray.getByName('RSetupT').value
        if(argArray.getByName('SPeriod') != None):
            chanTEDS.SPeriod = argArray.getByName('SPeriod').value
        if(argArray.getByName('WarmUpT') != None):
            chanTEDS.WarmUpT = argArray.getByName('WarmUpT').value
        if(argArray.getByName('RDelayT') != None):
            chanTEDS.RDelayT = argArray.getByName('RDelayT').value
        if(argArray.getByName('TestTime') != None):
            chanTEDS.TestTime = argArray.getByName('TestTime').value
        if(argArray.getByName('TimeSrc') != None):
            chanTEDS.TimeSrc = argArray.getByName('TimeSrc').value
        if(argArray.getByName('InPropDl') != None):
            chanTEDS.InPropDl = argArray.getByName('InPropDl').value
        if(argArray.getByName('OutPropD') != None):
            chanTEDS.OutPropD = argArray.getByName('OutPropD').value
        if(argArray.getByName('TSError') != None):
            chanTEDS.TSError = argArray.getByName('TSError').value
        if(argArray.getByName('Sampling') != None):
            chanTEDS.Sampling = Sampling.from_argumentArray(argArray.getByName('Sampling').value)
        if(argArray.getByName('DataXmit') != None):
            chanTEDS.DataXmit = argArray.getByName('DataXmit').value
        if(argArray.getByName('Buffered') != None):
            chanTEDS.Buffered = argArray.getByName('Buffered').value
        if(argArray.getByName('EndOfSet') != None):
            chanTEDS.EndOfSet = argArray.getByName('EndOfSet').value
        if(argArray.getByName('EdgeRpt') != None):
            chanTEDS.EdgeRpt = argArray.getByName('EdgeRpt').value
        if(argArray.getByName('ActHalt') != None):
            chanTEDS.ActHalt = argArray.getByName('ActHalt').value
        if(argArray.getByName('Direction') != None):
            chanTEDS.Direction = argArray.getByName('Direction').value
        if(argArray.getByName('DAngles') != None):
            chanTEDS.DAngles = argArray.getByName('DAngles').value
        if(argArray.getByName('ESOption') != None):
            chanTEDS.ESOption = argArray.getByName('CalESOptioney').value

        return chanTEDS


class PhyUnits:
    
    def __init__(self):

        self.UnitType = None
        self.Radians = None
        self.SterRad = None
        self.Meters = None
        self.Kilogram = None
        self.Seconds = None
        self.Amperes = None
        self.Kelvins = None
        self.Moles = None
        self.Candelas = None
        self.UnitsExt = None
    

    def getName(self):
        if(self.UnitType == 0 and self.Kelvins == 130):
            return "TEMPERATURE"
        return None


    def to_TVL(self, type, tuple_length):

        barray = bytearray()

        if(self.UnitType != None):      
            tvlUnitType = teds.TEDS_TLV_Block(50, 1, self.UnitType.to_bytes(1, 'big'))
            barray.extend(tvlUnitType.to_bytes(tuple_length))
        if(self.Radians != None):      
            tvlRadians = teds.TEDS_TLV_Block(51, 1, self.Radians.to_bytes(1, 'big'))
            barray.extend(tvlRadians.to_bytes(tuple_length))
        if(self.SterRad != None):      
            tvlSterRad = teds.TEDS_TLV_Block(52, 1, self.SterRad.to_bytes(1, 'big'))
            barray.extend(tvlSterRad.to_bytes(tuple_length))
        if(self.Meters != None):      
            tvlMeters = teds.TEDS_TLV_Block(53, 1, self.Meters.to_bytes(1, 'big'))
            barray.extend(tvlMeters.to_bytes(tuple_length))
        if(self.Kilogram != None):      
            tvlKilogram = teds.TEDS_TLV_Block(54, 1, self.Kilogram.to_bytes(1, 'big'))
            barray.extend(tvlKilogram.to_bytes(tuple_length))
        if(self.Seconds != None):      
            tvlSeconds = teds.TEDS_TLV_Block(55, 1, self.Seconds.to_bytes(1, 'big'))
            barray.extend(tvlSeconds.to_bytes(tuple_length))
        if(self.Amperes != None):      
            tvlAmperes = teds.TEDS_TLV_Block(56, 1, self.Amperes.to_bytes(1, 'big'))
            barray.extend(tvlAmperes.to_bytes(tuple_length))
        if(self.Kelvins != None):      
            tvlKelvins = teds.TEDS_TLV_Block(57, 1, self.Kelvins.to_bytes(1, 'big'))
            barray.extend(tvlKelvins.to_bytes(tuple_length))
        if(self.Moles != None):      
            tvlMoles = teds.TEDS_TLV_Block(58, 1, self.Moles.to_bytes(1, 'big'))
            barray.extend(tvlMoles.to_bytes(tuple_length))
        if(self.Candelas != None):      
            tvlCandelas = teds.TEDS_TLV_Block(59, 1, self.Candelas.to_bytes(1, 'big'))
            barray.extend(tvlCandelas.to_bytes(tuple_length))
        if(self.UnitsExt != None):      
            tvlUnitsExt = teds.TEDS_TLV_Block(60, 1, self.UnitsExt.to_bytes(1, 'big'))
            barray.extend(tvlUnitsExt.to_bytes(tuple_length))

        return teds.TEDS_TLV_Block(type, len(barray), barray)

    def to_argumentArray(self):

        argArray = ArgumentArray()

        if(self.UnitType != None):      
            argArray.putByName('UnitType', Argument(TypeCode.UINT8_TC, self.UnitType))            
        if(self.Radians != None):      
            argArray.putByName('Radians', Argument(TypeCode.UINT8_TC, self.Radians))            
        if(self.SterRad != None):      
            argArray.putByName('SterRad', Argument(TypeCode.UINT8_TC, self.SterRad))            
        if(self.Meters != None):      
            argArray.putByName('Meters ', Argument(TypeCode.UINT8_TC, self.Meters))            
        if(self.Kilogram != None):      
            argArray.putByName('Kilogram', Argument(TypeCode.UINT8_TC, self.Kilogram))            
        if(self.Seconds != None):      
            argArray.putByName('Seconds', Argument(TypeCode.UINT8_TC, self.Seconds))            
        if(self.Amperes != None):      
            argArray.putByName('Amperes', Argument(TypeCode.UINT8_TC, self.Amperes))            
        if(self.Kelvins != None):      
            argArray.putByName('Kelvins', Argument(TypeCode.UINT8_TC, self.Kelvins))            
        if(self.Moles != None):      
            argArray.putByName('Moles', Argument(TypeCode.UINT8_TC, self.Moles))            
        if(self.Candelas != None):      
            argArray.putByName('Candelas', Argument(TypeCode.UINT8_TC, self.Candelas))            
        if(self.UnitsExt != None):      
            argArray.putByName('UnitsExt', Argument(TypeCode.UINT8_TC, self.UnitsExt))     

        return argArray
    
    def from_bytes(barray, tLength):

        size = len(barray)
        index = 0
        
        phyUnits = PhyUnits()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 50):
                phyUnits.UnitType = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 51):
                phyUnits.Radians = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 52):
                phyUnits.SterRad = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 53):
                phyUnits.Meters = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 54):
                phyUnits.Kilogram = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 55):
                phyUnits.Seconds = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 56):
                phyUnits.Amperes = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 57):
                phyUnits.Kelvins = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 58):
                phyUnits.Moles = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 59):
                phyUnits.Candelas = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 60):
                phyUnits.UnitsExt = int.from_bytes(tvl.value, 'big')

        return phyUnits

    def from_argumentArray(argArray):
        
        phyUnits = PhyUnits()

        if(argArray.getByName('UnitType') != None):
            phyUnits.UnitType = argArray.getByName('UnitType').value
        if(argArray.getByName('Radians') != None):
            phyUnits.Radians = argArray.getByName('Radians').value
        if(argArray.getByName('SterRad') != None):
            phyUnits.SterRad = argArray.getByName('SterRad').value
        if(argArray.getByName('Meters') != None):
            phyUnits.Meters = argArray.getByName('Meters').value
        if(argArray.getByName('Kilogram') != None):
            phyUnits.Kilogram = argArray.getByName('Kilogram').value
        if(argArray.getByName('Seconds') != None):
            phyUnits.Seconds = argArray.getByName('Seconds').value
        if(argArray.getByName('Amperes') != None):
            phyUnits.Amperes = argArray.getByName('Amperes').value
        if(argArray.getByName('Kelvins') != None):
            phyUnits.Kelvins = argArray.getByName('Kelvins').value
        if(argArray.getByName('Moles') != None):
            phyUnits.Moles = argArray.getByName('Moles').value
        if(argArray.getByName('Candelas') != None):
            phyUnits.Candelas = argArray.getByName('Candelas').value
        if(argArray.getByName('UnitsExt') != None):
            phyUnits.UnitsExt = argArray.getByName('UnitsExt').value
        
        return phyUnits

class Sample:

    def __init__(self):

        self.DatModel = None
        self.ModLength = None
        self.SigBits = None

    def to_TVL(self, type, tuple_length):

        barray = bytearray()

        if(self.DatModel != None):      
            tvlDatModel = teds.TEDS_TLV_Block(40, 1, self.DatModel.to_bytes(1, 'big'))
            barray.extend(tvlDatModel.to_bytes(tuple_length))
        if(self.ModLength != None):      
            tvlModLength = teds.TEDS_TLV_Block(41, 1, self.ModLength.to_bytes(1, 'big'))
            barray.extend(tvlModLength.to_bytes(tuple_length))
        if(self.SigBits != None):      
            tvlSigBits = teds.TEDS_TLV_Block(42, 2, self.SigBits.to_bytes(2, 'big'))
            barray.extend(tvlSigBits.to_bytes(tuple_length))

        return teds.TEDS_TLV_Block(type, len(barray), barray)

    def to_argumentArray(self):

        argArray = ArgumentArray()

        if(self.DatModel != None):      
            argArray.putByName('DatModel', Argument(TypeCode.UINT8_TC, self.DatModel))            
        if(self.ModLength != None):      
            argArray.putByName('ModLength', Argument(TypeCode.UINT8_TC, self.ModLength))            
        if(self.SigBits != None):      
            argArray.putByName('SigBits', Argument(TypeCode.UINT16_TC, self.SigBits))      

        return argArray
    
    def from_bytes(barray, tLength):

        size = len(barray)
        index = 0
        
        sample = Sample()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 40):
                sample.DatModel = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 41):
                sample.ModLength = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 42):
                sample.SigBits = int.from_bytes(tvl.value, 'big')

        return sample

    def from_argumentArray(argArray):
        
        sample = Sample()

        if(argArray.getByName('DatModel') != None):
            sample.DatModel = argArray.getByName('DatModel').value
        if(argArray.getByName('ModLength') != None):
            sample.ModLength = argArray.getByName('ModLength').value
        if(argArray.getByName('SigBits') != None):
            sample.SigBits = argArray.getByName('SigBits').value
        
        return sample

class DataSet:

    def __init__(self):

        self.Repeats = None
        self.SOrigin = None
        self.StepSize = None
        self.SUnits = None
        self.PreTrigg = None
        
    def to_TVL(self, type, tuple_length):

        barray = bytearray()

        if(self.Repeats != None):      
            tvlRepeats = teds.TEDS_TLV_Block(43, 2, self.Repeats.to_bytes(2, 'big'))
            barray.extend(tvlRepeats.to_bytes(tuple_length))
        if(self.SOrigin != None):      
            tvlSOrigin = teds.TEDS_TLV_Block(44, 4, struct.pack('>f', self.SOrigin))
            barray.extend(tvlSOrigin.to_bytes(tuple_length))
        if(self.StepSize != None):      
            tvlStepSize = teds.TEDS_TLV_Block(45, 4, struct.pack('>f', self.StepSize))
            barray.extend(tvlStepSize.to_bytes(tuple_length))
        if(self.SUnits != None):      
            tvlSUnits = self.SUnits.to_TVL(46, tuple_length)
            barray.extend(tvlSUnits.to_bytes(self.TEDSID.tuple_length))
        if(self.PreTrigg != None):      
            tvlPreTrigg = teds.TEDS_TLV_Block(47, 2, self.PreTrigg.to_bytes(2, 'big'))
            barray.extend(tvlPreTrigg.to_bytes(tuple_length))

        return teds.TEDS_TLV_Block(type, len(barray), barray)

    def to_argumentArray(self):

        argArray = ArgumentArray()

        if(self.Repeats != None):
            argArray.putByName('Repeats', Argument(TypeCode.UINT16_TC, self.Repeats))
        if(self.SOrigin != None):      
            argArray.putByName('SOrigin', Argument(TypeCode.FLOAT32_TC, self.SOrigin))
        if(self.StepSize != None):      
            argArray.putByName('StepSize', Argument(TypeCode.FLOAT32_TC, self.StepSize))
        if(self.SUnits != None):
            argArray.putByName('SUnits', Argument(TypeCode.ARGUMENT_ARRAY_TC, self.SUnits.to_argumentArray()))
        if(self.PreTrigg != None):
            argArray.putByName('PreTrigg', Argument(TypeCode.UINT16_TC, self.PreTrigg))
        
        return argArray
    
    def from_bytes(barray, tLength):

        size = len(barray)
        index = 0
        
        dataSet = DataSet()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 43):
                dataSet.Repeats = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 44):
                dataSet.SOrigin = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 45):
                dataSet.StepSize = struct.unpack('>f', tvl.value)[0]
            if(tvl.type == 46):
                dataSet.SUnits = PhyUnits.from_bytes(tvl.value, tLength)
            if(tvl.type == 47):
                dataSet.PreTrigg = int.from_bytes(tvl.value, 'big')

        return dataSet

    def from_argumentArray(argArray):
        
        dataSet = DataSet()

        if(argArray.getByName('Repeats') != None):
            dataSet.Repeats = argArray.getByName('Repeats').value
        if(argArray.getByName('SOrigin') != None):
            dataSet.SOrigin = argArray.getByName('SOrigin').value
        if(argArray.getByName('StepSize') != None):
            dataSet.StepSize = argArray.getByName('StepSize').value
        if(argArray.getByName('SUnits') != None):
            dataSet.SUnits = PhyUnits.from_argumentArray(argArray.getByName('SUnits').value)
        if(argArray.getByName('PreTrigg') != None):
            dataSet.PreTrigg = argArray.getByName('PreTrigg').value
        
        return dataSet
        

class Sampling:

    def __init__(self):
        
        self.SampMode = None
        self.SDefault = None

    def to_TVL(self, type, tuple_length):

        barray = bytearray()

        if(self.SampMode != None):      
            tvlSampMode = teds.TEDS_TLV_Block(48, 1, self.SampMode.to_bytes(1, 'big'))
            barray.extend(tvlSampMode.to_bytes(tuple_length))
        if(self.SDefault != None):      
            tvlSDefault = teds.TEDS_TLV_Block(49, 1, self.SDefault.to_bytes(1, 'big'))
            barray.extend(tvlSDefault.to_bytes(tuple_length))

        return teds.TEDS_TLV_Block(type, len(barray), barray)

    def to_argumentArray(self):

        argArray = ArgumentArray()

        if(self.SampMode != None):      
            argArray.putByName('SampMode', Argument(TypeCode.UINT8_TC, self.SampMode))            
        if(self.SDefault != None):      
            argArray.putByName('SDefault', Argument(TypeCode.UINT8_TC, self.SDefault))            

        return argArray
    
    def from_bytes(barray, tLength):

        size = len(barray)
        index = 0
        
        sampling = Sampling()

        while(index < size):
            tvl = teds.TEDS_TLV_Block.from_bytes(barray[index:], tLength)
            index = index + 1 + tLength + tvl.length

            if(tvl.type == 48):
                sampling.SampMode = int.from_bytes(tvl.value, 'big')
            if(tvl.type == 49):
                sampling.SDefault = int.from_bytes(tvl.value, 'big')

        return sampling

    def from_argumentArray(argArray):
        
        sampling = Sampling()

        if(argArray.getByName('SampMode') != None):
            sampling.SampMode = argArray.getByName('SampMode').value
        if(argArray.getByName('SDefault') != None):
            sampling.SDefault = argArray.getByName('SDefault').value

        return sampling