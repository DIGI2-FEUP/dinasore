from opc_ua import peer
from data_model import service_set
from data_model import point_set
from data_model import ua_set
from data_model import utils
from data_model import monitor
import xml.etree.ElementTree as ETree
import os
import sys
import logging


class UaManager(peer.UaPeer):

    def __init__(self, address, file_name):
        self.file_name = file_name

        # parse the xml
        logging.info('getting the xml self definition...')
        try:
            self.xml_path = os.path.join(os.path.dirname(sys.path[0]), 'resources')
            # Reads the xml
            tree = ETree.parse(os.path.join(self.xml_path, self.file_name))
            # Gets the root element
            self.root_xml = tree.getroot()
            # parse the header
            for base_element in self.root_xml:
                # splits the tag in these 3 camps
                uri, ignore, tag = base_element.tag[1:].partition("}")
                if tag == 'general':
                    for item in base_element:
                        if item.attrib['id'] == 'SMART_OBJECT_NAME':
                            self.base_name = item.text

        except FileNotFoundError as error:
            logging.error('can not find the self definition file')
            logging.error(error)
        else:
            logging.info('self definition (xml) imported from: {0}'.format(os.path.join(self.xml_path,
                                                                                        'data_model.xml')))

        # initializes the peer: server opc-ua
        peer.UaPeer.__init__(self, address, server_name=self.base_name)

    def __call__(self, config):
        # base idx for the opc-ua nodeId
        self.base_idx = 'ns=2;s={0}'.format(self.base_name)

        # creates the root object 'SmartObject'
        self.create_object(2, self.base_name, path=self.generate_path([(0, 'Objects')]))

        # creates the path to that object
        self.ROOT_LIST = [(0, 'Objects'), (2, self.base_name)]
        self.ROOT_PATH = self.generate_path(self.ROOT_LIST)

        # configuration (connection to 4diac code)
        self.config = config

        # pointers to all the sets
        self.ua_sets = {'deviceset': ua_set.UaSet(self, set_xml_name='DeviceSet', item_xml_name='device',
                                                  loop_type=True),
                        'serviceinstanceset': ua_set.UaSet(self, set_xml_name='ServiceInstanceSet',
                                                           item_xml_name='serviceinstance'),
                        'servicedescriptionset': service_set.ServiceSet(self),
                        'pointdescriptionset': point_set.PointSet(self)}

        # creates the properties
        self.__create_properties()

        # create the monitor hardware variables
        self.monitor_hardware = monitor.MonitorSystem(self)
        self.monitor_hardware.start()

    def from_xml(self):
        xml_items = {}
        for base_element in self.root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")

            if tag != 'general':
                # parses each set
                self.ua_sets[tag].from_xml(base_element)
                xml_items[tag] = base_element

        # parses the subscriptions
        self.ua_sets['deviceset'].parse_all_subscriptions(xml_items['deviceset'])
        self.ua_sets['serviceinstanceset'].parse_all_subscriptions(xml_items['serviceinstanceset'])
        self.ua_sets['pointdescriptionset'].parse_all_subscriptions(xml_items['pointdescriptionset'])

        # checks if is needed to change any ua name
        self.check_ua_names()

        self.config.start_work()

    def from_fb(self, fb, fb_xml):
        item_type = fb_xml.attrib['OpcUa'].split('.')

        if item_type[0] == 'DEVICE':
            self.ua_sets['deviceset'].from_fb(fb, fb_xml)

        elif item_type[0] == 'SERVICE':
            # first check if needs to create the service
            self.ua_sets['servicedescriptionset'].from_fb(fb.fb_type, fb_xml)
            # after create the instance
            self.ua_sets['serviceinstanceset'].from_fb(fb, fb_xml)

        elif item_type[0] == 'POINT':
            self.ua_sets['pointdescriptionset'].from_fb(fb, fb_xml, point_type=item_type[1])

    def save_xml(self):
        root_xml = ETree.Element('smartobjectselfdescription',
                                 attrib={'xmlns': 'http://systec-fof.fe.up.pt/sosd',
                                         'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        tree_xml = ETree.ElementTree(root_xml)
        # get the general data
        for base_element in self.root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")
            if tag == 'general':
                # creates the general tag
                general_xml = ETree.SubElement(root_xml, 'general')
                for data_element in base_element:
                    data_xml = ETree.SubElement(general_xml, 'data')
                    data_xml.attrib['id'] = data_element.attrib['id']
                    data_xml.attrib['DataType'] = data_element.attrib['DataType']
                    data_xml.attrib['ValueRank'] = data_element.attrib['ValueRank']
                    if data_xml.attrib['id'] == 'SMART_OBJECT_NAME':
                        data_xml.text = self.base_name
                    else:
                        data_xml.text = data_element.text

        xml_dict = {'deviceset': ETree.SubElement(root_xml, 'deviceset'),
                    'pointdescriptionset': ETree.SubElement(root_xml, 'pointdescriptionset'),
                    'servicedescriptionset': ETree.SubElement(root_xml, 'servicedescriptionset'),
                    'serviceinstanceset': ETree.SubElement(root_xml, 'serviceinstanceset')}

        # write in the copy data model
        tree_xml.write(os.path.join(self.xml_path, 'data_model_copy.xml'))

        for set_name, set_item in self.ua_sets.items():
            # saves the set
            set_item.save_xml(xml_dict[set_name])

        # writes the xml to the respective file
        tree_xml.write(os.path.join(self.xml_path, self.file_name))

    def __create_properties(self):
        for base_element in self.root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")

            if tag == 'general':
                for item in base_element:
                    # adds the property to the opc-ua server
                    utils.default_property(self, self.base_idx, self.ROOT_PATH,
                                           property_name=item.attrib['id'], property_value=item.text)

    def create_ua_connection(self, source, destination):
        # splits both source and destination (fb, fb_variable)
        destination_attr = destination.split(sep='.')

        fb_dict = {**self.ua_sets['deviceset'].items_dict,
                   **self.ua_sets['pointdescriptionset'].items_dict,
                   **self.ua_sets['serviceinstanceset'].items_dict}

        if destination_attr[0] in fb_dict:
            fb_dict[destination_attr[0]].fb_connection_subscription(source, destination)

    def write_ua_connection(self, source_value, destination):
        # splits both source and destination (fb, fb_variable)
        destination_attr = destination.split(sep='.')

        fb_dict = {**self.ua_sets['deviceset'].items_dict,
                   **self.ua_sets['pointdescriptionset'].items_dict,
                   **self.ua_sets['serviceinstanceset'].items_dict}

        if destination_attr[0] in fb_dict:
            fb_dict[destination_attr[0]].fb_write_subscription(source_value, destination)

    def check_ua_names(self):
        fb_dict = {**self.ua_sets['deviceset'].items_dict,
                   **self.ua_sets['pointdescriptionset'].items_dict,
                   **self.ua_sets['serviceinstanceset'].items_dict}

        # iterates over the dict
        for key, item in fb_dict.items():
            # for each item verify
            item.refract_ua_name()
            # check also the equipment
            item.refract_ua_equipment()

    def stop_ua(self):
        # stops the monitor thread
        self.monitor_hardware.stop()
        # stops the configuration work
        self.config.stop_work()
        # stops the ua server
        self.stop()
