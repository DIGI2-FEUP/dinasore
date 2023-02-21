from core import configuration
from xml.etree import ElementTree as ETree
import time
import struct
import logging
import gc
import os
import sys
import shutil
import re


class Manager:

    def __init__(self):
        self.start_time = time.time() * 1000
        self.config_dictionary = dict()
        # attributes responsible for the ua integration
        self.file_name = None
        # stores the requests structure
        self.requests = []
        self.write_fboot = False
        self.fboot_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model.fboot')

    def get_config(self, config_id):
        fb_element = None
        try:
            fb_element = self.config_dictionary[config_id]
        except KeyError as error:
            logging.error('can not find that configuration (4DIAC resource)')
            logging.error(error)
        return fb_element

    def set_config(self, config_id, config_element):
        self.config_dictionary[config_id] = config_element

    def store_request(self, req, config_id=None):
        # converts the type
        if type(req) == bytes:
            req = req.decode('utf-8')
        # removes the new line characters
        req = re.sub('\s+', ' ', req)
        # if is active the fboot writing
        if self.write_fboot:
            # adds the request with no config name
            if config_id is None:
                self.requests.append(';{0}'.format(req))
            # adds with the config at the beginning
            else:
                self.requests.append('{0};{1}'.format(config_id, req))

    def parse_general(self, xml_data):
        # Parses the xml
        element = ETree.fromstring(xml_data)
        action = element.attrib['Action']
        request_id = element.attrib['ID']
        xml = None

        if action == 'CREATE':
            # Iterate over the list of children
            for child in element:
                # Create configuration (function block)
                if child.tag == 'FB':
                    conf_name = child.attrib['Name']
                    conf_type = child.attrib['Type']
                    # Stops the configuration
                    for config_name, config in self.config_dictionary.items():
                        config.stop_work()
                    self.config_dictionary = dict()
                    if conf_name not in self.config_dictionary:
                        # Creates the configuration
                        config = configuration.Configuration(conf_name, conf_type)
                        self.write_fboot = True
                        self.set_config(conf_name, config)
                        self.store_request(xml_data)

        elif action == 'QUERY':
            pass

        elif action == 'READ':
            # Iterate over the list of children
            for child in element:
                # Reads values from a watch
                if child.tag == 'Watches':
                    xml = ETree.Element('Watches')
                    # Gets all the watches from all the xml_data
                    for config_id, config in self.config_dictionary.items():
                        resource_xml, resource_len = config.read_watches(self.start_time)
                        # Appends only if has anything
                        if resource_len > 0:
                            xml.append(resource_xml)

                    resources_len = len(xml.findall('Resource'))
                    # If doesn't have any resource
                    if resources_len < 0:
                        xml = None

        elif action == 'KILL':
            # Iterate over the list of children
            for child in element:
                # Kill a configuration (could be a fb)
                if child.tag == 'FB':
                    fb_name = child.attrib['Name']
                    # Checks if exists the configuration
                    if fb_name in self.config_dictionary:
                        # Stops the configuration
                        for config_name, config in self.config_dictionary.items():
                            config.stop_work()
                        # Release memory
                        gc.collect()
            # If we want to kill the device
            if len(element) == 0:
                pass

        elif action == 'DELETE':
            # Iterate over the list of children
            for child in element:
                # Deletes a configuration (could be a fb)
                if child.tag == 'FB':
                    # conf_name = child.attrib['Name']
                    # Checks if exists the configuration
                    # if conf_name in self.config_dictionary:
                    self.config_dictionary = dict()
                    # Deletes the configuration
                    # self.stop_all()
                    # Release memory
                    gc.collect()
            # reset the program
            resources_path = os.path.join(os.path.dirname(sys.path[0]), 'resources')
            os.remove(os.path.join(resources_path, 'data_model.fboot'))
            shutil.copyfile(os.path.join(resources_path, 'data_model_copy.fboot'),
                            os.path.join(resources_path, 'data_model.fboot'))

        response = self.build_response(request_id, xml)
        return response

    def parse_configuration(self, xml_data, config_id):
        # replace all ['] except the ones preceded by a $ --> [&apos;] -> " ", [$&apos;] --> " ' "
        # treated_xml = re.sub("[$]{1}'{1}", "'", re.sub("(?<![$])'", "", xml_data.replace("&apos;", "'")))
        # Parses the xml
        element = ETree.fromstring(xml_data)
        action = element.attrib['Action']
        request_id = element.attrib['ID']

        if action == 'CREATE':
            # Iterate over the list of children
            for child in element:
                # Create function block
                if child.tag == 'FB':
                    fb_name = child.attrib['Name']
                    fb_type = child.attrib['Type']
                    self.get_config(config_id).create_fb(fb_name, fb_type)
                    self.store_request(xml_data, config_id)

                # Create connection
                elif child.tag == 'Connection':
                    connection_source = child.attrib['Source']
                    connection_destination = child.attrib['Destination']
                    self.get_config(config_id).create_connection(connection_source, connection_destination)
                    self.store_request(xml_data, config_id)

                # Create watch
                elif child.tag == 'Watch':
                    watch_source = child.attrib['Source']
                    watch_destination = child.attrib['Destination']
                    self.get_config(config_id).create_watch(watch_source, watch_destination)

        elif action == 'DELETE':
            # Iterate over the list of children
            for child in element:
                # Delete watch
                if child.tag == 'Watch':
                    watch_source = child.attrib['Source']
                    watch_destination = child.attrib['Destination']
                    self.get_config(config_id).delete_watch(watch_source, watch_destination)

        elif action == 'START':
            # saves the actual configuration on fboot file
            self.store_request(xml_data, config_id)
            self.save_fboot()
            self.requests = []
            self.write_fboot = False
            # Starts the configuration
            self.get_config(config_id).start_work()
        
        elif action == 'WRITE':
            # Iterate over the list of children
            for child in element:
                # Write a connection with value
                if child.tag == 'Connection':
                    connection_source = child.attrib['Source']
                    connection_destination = child.attrib['Destination']
                    self.get_config(config_id).write_connection(connection_source, connection_destination)
                    self.store_request(xml_data, config_id)

        response = self.build_response(request_id, None)
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

    class InvalidFbootState(Exception):
        pass

    def build_fboot(self):
        # Check if data model file exists and is not empty
        try:
            file = open(self.fboot_path, 'r')
        except FileNotFoundError:
            logging.warning('Could not find fboot definition file. Awaiting deployment.')
        else:
            if os.stat(self.fboot_path).st_size == 0:
                logging.warning('Fboot definition file is empty. Awaiting deployment')
            else:
                try:
                    # Parse data model file
                    lines = file.readlines()
                    file.close()
                    self.parse_fboot(lines)
                except self.InvalidFbootState:
                    logging.error('Fboot definition file is in an invalid state. Awaiting deployment')

    def parse_fboot(self, lines):
        for line in lines:
            # splits the line
            chunks = line.split(';')
            if len(chunks) != 2:
                raise self.InvalidFbootState
            # checks if is the msg to create config
            if chunks[0] == '':
                self.parse_general(chunks[1])
            # checks if is to create fb or connection
            else:
                self.parse_configuration(chunks[1], chunks[0])

    def save_fboot(self):
        file = open(self.fboot_path, 'w')
        for request in self.requests:
            file.write(request)
            file.write('\n')
        file.close()

    def stop(self):
        for _, config in self.config_dictionary.items():
            config.stop_work()
