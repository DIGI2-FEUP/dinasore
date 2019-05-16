from core import manager
from core import configuration
from opc_ua import peer
from data_model import device
import xml.etree.ElementTree as ETree
import os
import sys
import logging


class UaManager(peer.UaPeer):

    def __init__(self, address, diac_manager):
        peer.UaPeer.__init__(self, address)
        self.diac_manager = diac_manager
        self.xml_path = os.path.join(os.path.dirname(sys.path[0]),
                                     'resources',
                                     'data_model_opcua.xml')
        # self.import_xml(path=self.xml_path)

        # creates the root object 'SmartObject'
        self.create_object(2, 'SmartObject')
        # creates the path to that object
        self.ROOT_PATH = self.generate_path([(2, 'SmartObject')])

        self.device_set = device.DeviceSet()

    def parse_xml(self):
        logging.info('getting the xml self definition...')

        try:
            # Reads the xml
            tree = ETree.parse(self.xml_path)
            # Gets the root element
            root = tree.getroot()

            if root[0].tag == 'general':
                config = self.parse_general(root[0])

                for base_element in root:
                    if base_element.tag == 'deviceset':
                        self.device_set.parse_xml(base_element, config)

                    elif base_element.tag == 'serviceinstanceset':
                        pass

                    elif base_element.tag == 'servicedescriptionset':
                        pass

                    elif base_element.tag == 'pointdescriptionset':
                        pass

        except FileNotFoundError as error:
            logging.error('can not find the self definition file')
            logging.error(error)
        else:
            logging.info('self definition (xml) imported from: {0}'.format(self.xml_path))

    def parse_general(self, general_root):
        config_id, config_type = '', 'EMB_RES'

        for item in general_root:
            if item.attrib['SMART_OBJECT_NAME'] in item:
                # uses the name of the so as config_id
                config_id = item.attrib['SMART_OBJECT_NAME']

        config = configuration.Configuration(config_id, config_type)
        self.diac_manager.set_config(config_id, config)
        return config


man = manager.Manager()
base = UaManager('opc.tcp://localhost:4841', man)
