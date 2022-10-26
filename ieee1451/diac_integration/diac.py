from ieee1451.diac_integration.util import Diac_Util
from ieee1451.ncap.teds.teds import TEDS_ACCESS_CODES
from ieee1451.ncap.teds.geo_teds import *

from sys import platform
import os

class DIAC_Manager:
    
    def __init__(self, ncap_address, diac_address, port_diac):

        self.ncap_address = ncap_address
        self.port_diac = port_diac

        if(platform == "win32"):
            self.workspace = "//" + diac_address + "/diac_workspace/workspace"
        elif(platform == "linux" or platform == "linux2"):
            cmd = "sudo umount /mnt/diac_workspace"
            os.system(cmd)
            cmd = "sudo mount.cifs //" + diac_address + "/diac_workspace /mnt/diac_workspace " # if necessary add '-o \"user=User,password=Password\"'
            os.system(cmd)
            self.workspace = "/mnt/diac_workspace"
        
        self.project = "DissApp"
        self.system = "DissApp.sys"

        self.filepath = self.workspace + '/' + self.project + '/' + self.system
        self.subApp = None

        Diac_Util.clearWorkspace(self.filepath)


    def update(self, transducer):

            chanTeds = transducer.getTEDS(TEDS_ACCESS_CODES.ChanTEDS).data_block
            chanName = chanTeds.PhyUnits.getName()

            geoLocTeds = transducer.tim.getTEDS(TEDS_ACCESS_CODES.GeoLocTEDS).data_block
            geoLoc = GeoLoc_Util.xmlText2PosXY(geoLocTeds.XMLText)
            
            tim_uuid = transducer.tim.getTEDS(TEDS_ACCESS_CODES.MetaTEDS).data_block.UUID      # Convert UUID to String here if necessary!!!

            if(chanTeds.ChanType == 0):
                Diac_Util.addIEEE1451Block(self.ncap_address, self.port_diac, self.filepath, chanName, tim_uuid, transducer.id, geoLoc[0], geoLoc[1], chanName)


if (__name__ == '__main__'):

    diac = DIAC_Manager()