from opc_ua import peer
from data_model import device_set
from data_model import service_set
from data_model import point_set
from data_model import utils
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
        self.devices_set = device_set.DeviceSet(self)
        self.services_set = service_set.ServiceSet(self)
        self.points_set = point_set.PointSet(self)
        self.instances_set = service_set.InstanceSet(self)

        # parse the xml
        logging.info('getting the xml self definition...')
        try:
            self.xml_path = os.path.join(os.path.dirname(sys.path[0]),
                                         'resources', file_name)
            # Reads the xml
            tree = ETree.parse(self.xml_path)
            # Gets the root element
            self.root_xml = tree.getroot()

        except FileNotFoundError as error:
            logging.error('can not find the self definition file')
            logging.error(error)
        else:
            logging.info('self definition (xml) imported from: {0}'.format(self.xml_path))

        # creates the properties
        self.__create_properties()

    def from_xml(self):
        device_xml, service_xml, instance_xml, point_xml = None, None, None, None
        for base_element in self.root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = base_element.tag[1:].partition("}")
            # parses the device set
            if tag == 'deviceset':
                device_xml = base_element
            # parses the service description set
            elif tag == 'servicedescriptionset':
                service_xml = base_element
            # parses the service instance set
            elif tag == 'serviceinstanceset':
                instance_xml = base_element
            # parses the point description
            elif tag == 'pointdescriptionset':
                point_xml = base_element

        # parses in a ordered way
        self.devices_set.from_xml(device_xml)
        self.points_set.parse_xml_startpoint(point_xml)
        self.services_set.from_xml(service_xml)
        self.instances_set.from_xml(instance_xml)
        self.points_set.parse_xml_endpoint(point_xml)

        self.config.start_work()

    def from_fb(self, fb, fb_xml):
        device_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
            utils.parse_fb_description(fb_xml)
        item_type = device_type.split('.')

        if item_type[0] == 'DEVICE':
            self.devices_set.from_fb(fb, fb_xml)

        elif item_type[0] == 'SERVICE':
            # first check if needs to create the service
            self.services_set.from_fb(fb.fb_type, fb_xml)
            # after create the instance
            self.instances_set.from_fb(fb, fb_xml)

        elif item_type[0] == 'POINT':
            self.points_set.from_fb(fb, fb_xml, point_type=item_type[1])

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
                    data_xml.text = data_element.text

        # saves the device set
        device_set_xml = ETree.SubElement(root_xml, 'deviceset')
        self.devices_set.save_xml(device_set_xml)
        # saves the point set
        point_set_xml = ETree.SubElement(root_xml, 'pointdescriptionset')
        self.points_set.save_xml(point_set_xml)
        # saves the service set and the respective instances
        service_set_xml = ETree.SubElement(root_xml, 'servicedescriptionset')
        self.services_set.save_xml(service_set_xml)
        instance_set_xml = ETree.SubElement(root_xml, 'serviceinstanceset')
        self.instances_set.save_xml(instance_set_xml)
        # writes the xml to the respective file
        tree_xml.write(self.xml_path)

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
        fb = self.config.get_fb(destination_attr[0])

        fb_dict = {**self.services_set.service_dict,
                   **self.instances_set.instances_dict,
                   **self.devices_set.devices_dict,
                   **self.points_set.points_dict}

        if destination_attr[0] in fb_dict:
            fb_dict[destination_attr[0]].fb_connection_subscription(source, destination)

    def write_ua_connection(self, source_value, destination):
        # splits both source and destination (fb, fb_variable)
        destination_attr = destination.split(sep='.')
        fb = self.config.get_fb(destination_attr[0])

        fb_dict = {**self.services_set.service_dict,
                   **self.instances_set.instances_dict,
                   **self.devices_set.devices_dict,
                   **self.points_set.points_dict}

        if destination_attr[0] in fb_dict:
            fb_dict[destination_attr[0]].fb_write_subscription(source_value, destination)

    def stop_ua(self):
        # stops the configuration work
        self.config.stop_work()
        # stops the ua server
        self.stop()
