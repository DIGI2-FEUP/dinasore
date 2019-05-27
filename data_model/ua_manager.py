from core import manager
from core import configuration
from opc_ua import peer
from data_model import device, service
import xml.etree.ElementTree as ETree
import os
import sys
import logging


class UaManager(peer.UaPeer):

    def __init__(self, address, set_config):
        """
        SmartObject             -> obj
            DEVICE_TYPE         -> prop
            SMART_OBJECT_ID     -> prop
            SMART_OBJECT_NAME   -> prop
            STATE               -> prop
            DeviceSet           -> folder
                Dev1            -> obj
                    Vars        -> folder
                    Methods     -> folder
            ServiceSet          -> folder
            ServiceInstanceSet  -> folder
            PointDescriptionSet -> folder

        :param address:
        :param set_config:
        """

        peer.UaPeer.__init__(self, address)
        # pointers to set a configuration
        self.__set_config = set_config
        # pointers to all the sets
        self.__device_set = None
        self.__service_set = None
        self.__point_set = None

        # configuration (connection to 4diac code)
        self.config = None
        # sc id, base idx for the opc-ua nodeId
        self.general_id, self.idx = '', ''

        # creates the root object 'SmartObject'
        self.create_object(2,
                           'SmartObject',
                           path=self.generate_path([(0, 'Objects')]))

        # creates the path to that object
        self.ROOT_LIST = [(0, 'Objects'), (2, 'SmartObject')]
        self.ROOT_PATH = self.generate_path(self.ROOT_LIST)

    def __create_sets(self):
        # creates all the sets
        self.__device_set = device.DeviceSet(self)
        self.__service_set = service.ServiceSet(self)

    def __parse_sets(self, root):
        for base_element in root:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")

            if tag == 'deviceset':
                self.__device_set.from_xml(base_element)

            elif tag == 'serviceinstanceset':
                pass

            elif tag == 'servicedescriptionset':
                pass

            elif tag == 'pointdescriptionset':
                pass

        self.config.start_work()

    def __parse_general(self, general_root):
        self.idx = general_root[2].text
        base_idx = 'ns=2;s={0}'.format(self.idx)
        for item in general_root:
            # uses the SMART_OBJECT_NAME as the config_id
            if item.attrib['id'] == 'SMART_OBJECT_NAME':
                self.config = configuration.Configuration(item.text, 'EMB_RES')
                self.__set_config(item.text, self.config)

            # adds the property to the opc-ua server
            browse_name = '2:{0}'.format(item.attrib['id'])
            idx = '{0}.{1}'.format(base_idx, item.attrib['id'])
            self.create_property(self.ROOT_PATH, idx, browse_name, item.text)

    def from_xml(self):
        logging.info('getting the xml self definition...')
        try:
            xml_path = os.path.join(os.path.dirname(sys.path[0]),
                                    'resources',
                                    'data_model.xml')
            # Reads the xml
            tree = ETree.parse(xml_path)
            # Gets the root element
            root = tree.getroot()

            # parses the general info
            self.__parse_general(root[0])
            # creates the sets
            self.__create_sets()
            # parses the rest of info
            self.__parse_sets(root)

        except FileNotFoundError as error:
            logging.error('can not find the self definition file')
            logging.error(error)
        else:
            logging.info('self definition (xml) imported from: {0}'.format(xml_path))


man = manager.Manager()
base = UaManager('opc.tcp://localhost:4841', man.set_config)
base.from_xml()
