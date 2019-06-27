from opc_ua import peer
from data_model import device_set, service_set, utils
import xml.etree.ElementTree as ETree
import os
import sys
import logging


class UaManager(peer.UaPeer):

    def __init__(self, base_name, address, config, file_name):
        peer.UaPeer.__init__(self, address)

        # base idx for the opc-ua nodeId
        self.base_idx = 'ns=2;s={0}'.format(base_name)

        # creates the root object 'SmartObject'
        self.create_object(2, base_name, path=self.generate_path([(0, 'Objects')]))

        # creates the path to that object
        self.ROOT_LIST = [(0, 'Objects'), (2, base_name)]
        self.ROOT_PATH = self.generate_path(self.ROOT_LIST)

        # configuration (connection to 4diac code)
        self.config = config

        # pointers to all the sets
        self.__device_set = device_set.DeviceSet(self)
        self.__service_set = service_set.ServiceSet(self)

        # parse the xml
        logging.info('getting the xml self definition...')
        try:
            xml_path = os.path.join(os.path.dirname(sys.path[0]),
                                    'resources', file_name)
            # Reads the xml
            tree = ETree.parse(xml_path)
            # Gets the root element
            self.root_xml = tree.getroot()

        except FileNotFoundError as error:
            logging.error('can not find the self definition file')
            logging.error(error)
        else:
            logging.info('self definition (xml) imported from: {0}'.format(xml_path))

        # creates the properties
        self.__create_properties()

    def from_xml(self):
        for base_element in self.root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")

            if tag == 'deviceset':
                self.__device_set.from_xml(base_element)
            elif tag == 'servicedescriptionset':
                self.__service_set.from_xml(base_element)
            elif tag == 'serviceinstanceset':
                self.__service_set.create_instances_from_xml(base_element)
            elif tag == 'pointdescriptionset':
                pass

        self.config.start_work()

    def from_fb(self, fb, fb_xml):
        device_id, device_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
                utils.parse_fb_description(fb_xml)
        item_type = device_type.split('.')

        if item_type[0] == 'DEVICE':
            self.__device_set.from_fb(fb, fb_xml)

        if item_type[0] == 'SERVICE':
            # first check if needs to create the service
            self.__service_set.from_fb(fb.fb_type, fb_xml)
            # after create the instance
            self.__service_set.create_instance_from_fb(fb, fb_xml)

    def __create_properties(self):
        for base_element in self.root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")

            if tag == 'general':
                for item in base_element:
                    # adds the property to the opc-ua server
                    utils.default_property(self, self.base_idx, self.ROOT_PATH,
                                           property_name=item.attrib['id'], property_value=item.text)

    def save_xml(self, file_name):
        pass

    def stop_ua(self):
        # stops the configuration work
        self.config.stop_work()
        # stops the ua server
        self.stop()

    def search_id(self, subs_id):
        # first searches between the device
        if subs_id in self.__device_set.devices_dict:
            device = self.__device_set.devices_dict[subs_id]
            return device
        elif subs_id in self.__service_set.instances_map:
            # gets the service_id
            service_id = self.__service_set.instances_map[subs_id]
            # then gets the instance
            instance = self.__service_set.service_dict[service_id].instances_dict[subs_id]
            return instance
        else:
            return None
