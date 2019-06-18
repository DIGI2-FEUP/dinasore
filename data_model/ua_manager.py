from core import configuration
from opc_ua import peer
from data_model import device_set, service_set, utils
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
        self.general_id, self.base_idx = '', ''

        # creates the root object 'SmartObject'
        self.create_object(2,
                           'SmartObject',
                           path=self.generate_path([(0, 'Objects')]))

        # creates the path to that object
        self.ROOT_LIST = [(0, 'Objects'), (2, 'SmartObject')]
        self.ROOT_PATH = self.generate_path(self.ROOT_LIST)

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

    def from_fb(self, fb, fb_xml):
        item_id, item_type = utils.read_description_from_fb(fb_xml)
        item_type = item_type.split('.')

        if item_type[0] == 'DEVICE':
            self.__device_set.from_fb(fb, fb_xml)

        if item_type[0] == 'SERVICE':
            # first check if needs to create the service
            self.__service_set.from_fb(fb.fb_type, fb_xml)
            # after create the instance
            self.__service_set.instances_from_fb(fb, fb_xml)

    def __parse_general(self, general_root):
        self.base_idx = 'ns=2;s={0}'.format(general_root[2].text)
        for item in general_root:
            # uses the SMART_OBJECT_NAME as the config_id
            if item.attrib['id'] == 'SMART_OBJECT_NAME':
                self.config = configuration.Configuration(item.text, 'EMB_RES')
                self.__set_config(item.text, self.config)

            # adds the property to the opc-ua server
            utils.default_property(self, self.base_idx, self.ROOT_PATH,
                                   property_name=item.attrib['id'], property_value=item.text)

    def __parse_sets(self, root):
        for base_element in root:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")

            if tag == 'deviceset':
                self.__device_set.from_xml(base_element)

            elif tag == 'servicedescriptionset':
                self.__service_set.from_xml(base_element)

            elif tag == 'serviceinstanceset':
                self.__service_set.instances_from_xml(base_element)

            elif tag == 'pointdescriptionset':
                pass

        self.config.start_work()

    def __create_sets(self):
        # creates all the sets
        self.__device_set = device_set.DeviceSet(self)
        self.__service_set = service_set.Services(self)

    def search_id(self, subs_id):
        # first searches between the device
        if subs_id in self.__device_set.devices_dict:
            device = self.__device_set.devices_dict[subs_id]
            return device
        elif subs_id in self.__service_set.instance_map:
            # gets the service_id
            service_id = self.__service_set.instance_map[subs_id]
            # then gets the instance
            instance = self.__service_set.service_dict[service_id].instances_dict[subs_id]
            return instance
        else:
            return None
