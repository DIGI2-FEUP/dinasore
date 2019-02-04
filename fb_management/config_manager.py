from fb_management import configuration
from xml.etree import ElementTree as ETree
import time
import struct


class ConfigManager:

    def __init__(self):
        self.start_time = time.time()*1000
        self.config_dictionary = dict()

    def create_configuration(self, config_id, config_type):
        # Checks if exists the configuration
        if config_id not in self.config_dictionary:
            config = configuration.Configuration(config_id, config_type)
            self.config_dictionary[config_id] = config

    def parse_configuration(self, xml_data):
        # Parses the xml
        element = ETree.fromstring(xml_data)
        action = element.attrib['Action']
        request_id = element.attrib['ID']
        xml = None

        if action == 'CREATE':
            # Iterate over the list of children
            for child in element:
                # Create function block
                if child.tag == 'FB':
                    fb_name = child.attrib['Name']
                    fb_type = child.attrib['Type']
                    self.create_configuration(fb_name, fb_type)

        elif action == 'QUERY':
            pass

        elif action == 'READ':
            # Iterate over the list of children
            for child in element:
                # Reads values from a watch
                if child.tag == 'Watches':
                    xml = ETree.Element('Watches')
                    # Gets all the watches from all the resources
                    for config_id, config in self.config_dictionary.items():
                        resource_xml, resource_len = config.read_watches(self.start_time)
                        # Appends only if has anything
                        if resource_len > 0:
                            xml.append(resource_xml)

                    resources_len = len(xml.findall('Resource'))
                    # If doesn't have any resource
                    if resources_len < 0:
                        xml = None

        response = self.build_response(request_id, xml)
        return response

    def parse_payload(self, xml_data, config_id):
        # Parses the xml
        element = ETree.fromstring(xml_data)
        action = element.attrib['Action']
        request_id = element.attrib['ID']
        xml = None

        if action == 'CREATE':
            # Iterate over the list of children
            for child in element:
                # Create function block
                if child.tag == 'FB':
                    fb_name = child.attrib['Name']
                    fb_type = child.attrib['Type']
                    self.config_dictionary[config_id].create_fb(fb_name, fb_type)

                # Create connection
                elif child.tag == 'Connection':
                    connection_source = child.attrib['Source']
                    connection_destination = child.attrib['Destination']
                    self.config_dictionary[config_id].create_connection(connection_source, connection_destination)

                # Create watch
                elif child.tag == 'Watch':
                    watch_source = child.attrib['Source']
                    watch_destination = child.attrib['Destination']
                    self.config_dictionary[config_id].create_watch(watch_source, watch_destination)

        elif action == 'DELETE':
            # Iterate over the list of children
            for child in element:
                # Delete watch
                if child.tag == 'Watch':
                    watch_source = child.attrib['Source']
                    watch_destination = child.attrib['Destination']
                    self.config_dictionary[config_id].delete_watch(watch_source, watch_destination)

        elif action == 'START':
            # Starts the configuration
            self.config_dictionary[config_id].start_work()

        elif action == 'WRITE':
            # Iterate over the list of children
            for child in element:
                # Write a connection with value
                if child.tag == 'Connection':
                    connection_source = child.attrib['Source']
                    connection_destination = child.attrib['Destination']
                    self.config_dictionary[config_id].create_connection(connection_source, connection_destination)

        elif action == 'READ':
            # Iterate over the list of children
            for child in element:
                # Reads values from a watch
                if child.tag == 'Watches':
                    resource_xml, resource_len = self.config_dictionary[config_id].read_watches(self.start_time)
                    if resource_len > 0:
                        xml = ETree.Element('Watches')
                        xml.append(resource_xml)

        response = self.build_response(request_id, xml)
        return response

    @staticmethod
    def build_response(request_id, xml_response):
        xml = ETree.Element('Response', {'ID': request_id})
        # Verifies if is a default response
        if xml_response is not None:
            xml.append(xml_response)

        response_xml = ETree.tostring(xml)
        hex_input = '{:04x}'.format(len(response_xml))
        second_byte = int(hex_input[0:2], 16)
        third_byte = int(hex_input[2:4], 16)
        response_len = struct.pack('BB', second_byte, third_byte)
        response_header = b''.join([b'\x50', response_len])

        response = b''.join([response_header, response_xml])
        return response
