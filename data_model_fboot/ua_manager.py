from opc_ua import peer
from xml.etree import ElementTree as ETree
from data_model_fboot import ua_object, monitor, utils, ua_method
import logging
import os
import sys

class UaManagerFboot(peer.UaPeer):

    class InvalidFbootState(Exception):
       pass

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.fboot_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model.fboot')
        self.base_name = 'DINASORE OPC-UA'
        self.endpoint = 'opc.tcp://{0}:{1}'.format(address, port)

        peer.UaPeer.__init__(self, address=self.endpoint)

        self.folders = dict()
        self.ua_objects = dict()
        self.method_names = []
        self.method_inputs = None
        self.method_outputs = None
        self.opcua_method_name = None

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
        # create the monitor hardware variables
        self.monitor_hardware = monitor.MonitorSystem(self)
        self.monitor_hardware.start()
        # create function blocks folder
        folder_idx, folder_path, folder_list = utils.default_folder(self, self.base_idx, self.ROOT_PATH, self.ROOT_LIST, 'FunctionBlocks')
        self.folders['FunctionBlocks'] = {
            'idx': folder_idx,
            'path': folder_path,
            'path_list': folder_list
        }
        # create services folder 
        folder_idx, folder_path, folder_list = utils.default_folder(self, self.base_idx, self.ROOT_PATH, self.ROOT_LIST, 'OPC-UA_Methods')
        self.folders['OPC-UA_Methods'] = {
            'idx': folder_idx,
            'path': folder_path,
            'path_list': folder_list
        }

    def save_fboot(self, requests):
        file = open(self.fboot_path, 'w')
        start_fb = None
        is_watch = False
        for request in requests:
            element = ETree.fromstring(request)
            for child in element:
                if child.tag == 'Watch':
                    is_watch = True
                    break
            
            if is_watch:
                is_watch = False
                continue

            '''if start_fb is None:
                file.write(';')
                for child in element:
                    start_fb = child.attrib['Name']
            else:
                file.write('{0};'.format(start_fb))'''
            file.write(request)
            file.write('\n')
        file.close()

    def from_fboot(self):
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
                    self.parse_fboot(file)
                except self.InvalidFbootState:
                    logging.error('Fboot definition file is in an invalid state. Awaiting deployment')
                else:
                    if len(self.method_names) != 0:
                        self.method = ua_method.UaMethod(self, self.folders.get('OPC-UA_Methods'), self.method_root)
                    self.config.start_work()

    def parse_fboot(self, file):
        lines = file.readlines()
        file.close()
        # create function blocks - folders, objects and variables
        self.generate_function_blocks(lines)
        # create connections - write and create between variables and events
        self.generate_connections(lines)        

    def generate_function_blocks(self, lines):
        for line in lines:
            # Remove start fb from line
            #chunks = line.split(';')
            #if len(chunks) != 2:
            #    raise self.InvalidFbootState
            #xml_element = ETree.fromstring(chunks[1])
            xml_element = ETree.fromstring(line)
            try:
                if xml_element.get('Action') == 'CREATE':
                    for child in xml_element:
                        if child.tag == 'FB' and child.get('Type') != 'EMB_RES':
                            root_path = utils.get_fb_files_path(child.get('Type'))
                            # Check fbt file
                            fb_file = open(os.path.join(root_path, '{0}.fbt'.format(child.get('Type'))), 'r')
                            self.parse_fbt(child.get('Name'), fb_file)
            except KeyError:
                raise self.InvalidFbootState

    def generate_connections(self, lines):
        for line in lines:
            '''
            # Remove start fb from line
            chunks = line.split(';')
            if len(chunks) != 2:
                raise self.InvalidFbootState
            xml_element = ETree.fromstring(chunks[1])
            '''
            xml_element = ETree.fromstring(line)
            try:
                if xml_element.get('Action') == 'CREATE':
                    for child in xml_element:
                        if child.tag == 'Connection':
                            if len(self.method_names) == 0 or ( not utils.any_element_in_string(self.method_names, child.get('Source')) \
                                                                and not utils.any_element_in_string(self.method_names, child.get('Destination'))):
                                # Create connection
                                self.config.create_connection(child.get('Source'), child.get('Destination'))
                            elif len(self.method_names) != 0:
                                if utils.any_element_in_string(self.method_names, child.get('Source')):
                                    # Save event name to be triggered
                                    self.method_event = child.get('Destination')
                                elif utils.any_element_in_string(self.method_names, child.get('Destination')):
                                    # save name of final fb to execute
                                    self.method_final_fb = child.get('Source').split('.')[0]
                elif xml_element.get('Action') == 'WRITE':
                    for child in xml_element:
                        if child.tag == 'Connection':
                            if len(self.method_names) == 0 or not utils.any_element_in_string(self.method_names, child.get('Destination')):
                                # Write connection
                                self.config.write_connection(child.get('Source'), child.get('Destination'))    
                            elif len(self.method_names) != 0 and utils.any_element_in_string(self.method_names, child.get('Destination')):
                                # Save wrapper info
                                info_type = child.get('Destination').split('.')[1]
                                if info_type == 'INPUT':
                                    self.method_inputs = child.get('Source')
                                elif info_type == 'OUTPUT':
                                    self.method_outputs = child.get('Source')
                                elif info_type == 'METHOD_NAME':
                                    self.opcua_method_name = child.get('Source')                   
            except KeyError:
                raise self.InvalidFbootState

    def parse_fbt(self, fb_name, file):
        xml_tree = ETree.parse(file.name)
        xml_root = xml_tree.getroot()
        if xml_root.get('OpcUa') == 'METHOD':
            # set flag to create ua_method
            self.method_names.append(fb_name)
            self.method_root = xml_root
        else:
            # add ua object to dictionary
            item = ua_object.UaObject(self, self.folders.get('FunctionBlocks'), fb_name, xml_root)
            self.ua_objects[fb_name] = item
        file.close()

    def stop_ua(self):
        # stops the monitor thread
        self.monitor_hardware.stop()
        # stops the configuration work
        self.config.stop_work()
        # stops the ua server
        self.stop()
          
