from core import configuration
from data_model_fboot import ua_manager as ua_manager_fboot
from xml.etree import ElementTree as ETree
import time
import struct
import logging
import gc
import os
import sys
import shutil
import glob

class Manager:

    def __init__(self, monitor=None):
        self.start_time = time.time() * 1000
        self.config_dictionary = dict()
        self.monitor = monitor

        # attributes responsible for the ua integration
        self.ua_integration = False
        self.ua_url = 'opc.tcp://localhost:4041'
        self.manager_ua = None
        self.file_name = None

        # new opc-ua model variables
        self.requests = []

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

    def parse_general(self, xml_data):
        # Parses the xml
        element = ETree.fromstring(xml_data)
        action = element.attrib['Action']
        request_id = element.attrib['ID']
        xml = None

        if action == 'CREATE':
            self.requests.append(xml_data)

            ##############################################################
            ## remove all files in monitoring folder
            monitoring_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'monitoring', '')
            files = glob.glob("{0}*".format(monitoring_path))
            for f in files:
                os.remove(f)
            ##############################################################

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
                        config = configuration.Configuration(conf_name, conf_type, monitor=self.monitor)
                        self.set_config(conf_name, config)
                        # check the options for ua_integration
                        if self.ua_integration:
                            # add try catch OSError: [Errno 98] Address already in use
                            # first stop the previous manager
                            self.manager_ua_fboot.stop()

                            self.manager_ua_fboot = ua_manager_fboot.UaManagerFboot(self.manager_ua_fboot.address, self.manager_ua_fboot.port)
                            self.manager_ua_fboot(config)

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
            # check the options for ua_integration
            if self.ua_integration:
                # first stop the previous manager
                self.manager_ua.stop_ua()
            # If we want to kill the device
            if len(element) == 0:
                pass

        elif action == 'DELETE':

            ##############################################################
            ## remove all files in monitoring folder
            monitoring_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'monitoring', '')
            files = glob.glob("{0}*".format(monitoring_path))
            for f in files:
                os.remove(f)
            ##############################################################

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
            # check the options for ua_integration
            if self.ua_integration:

                # reset the program
                resources_path = os.path.join(os.path.dirname(sys.path[0]), 'resources')
                os.remove(os.path.join(resources_path, 'data_model.fboot'))
                shutil.copyfile(os.path.join(resources_path, 'data_model_copy.fboot'),
                                os.path.join(resources_path, 'data_model.fboot'))

                self.ua_manager_fboot = ua_manager_fboot.UaManagerFboot(self.ua_manager_fboot.address, self.ua_manager_fboot.port)
                config = configuration.Configuration('EMB_RES', 'EMB_RES')
                self.set_config('EMB_RES', config)
                self.ua_manager_fboot(config)

        response = self.build_response(request_id, xml)
        return response

    def parse_configuration(self, xml_data, config_id):
        # Parses the xml
        element = ETree.fromstring(xml_data)
        action = element.attrib['Action']
        request_id = element.attrib['ID']

        self.requests.append(xml_data)

        if action == 'CREATE':
            # Iterate over the list of children
            for child in element:
                # Create watch
                if child.tag == 'Watch':
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
            # check the options for ua_integration
            if self.ua_integration:
                # saves the actual configuration on fboot file
                self.manager_ua_fboot.save_fboot(self.requests)
                self.requests = []
                self.manager_ua_fboot.from_fboot()
        
        elif action == 'WRITE':
            # Iterate over the list of children
            for child in element:
                # Write a connection with value
                if child.tag == 'Connection' and child.attrib['Source'] == '$e':
                    connection_destination = child.attrib['Destination']
                    self.get_config(config_id).write_connection('$e', connection_destination)

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

    def build_ua_manager_fboot(self, address, port):
        self.manager_ua_fboot = ua_manager_fboot.UaManagerFboot(address, port)
        # creates the opc-ua manager
        config = configuration.Configuration('EMB_RES', 'EMB_RES', monitor=self.monitor)
        self.set_config('EMB_RES', config)
        # parses the description file
        self.manager_ua_fboot(config)
        self.manager_ua_fboot.from_fboot()
        self.ua_integration = True