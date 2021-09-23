from collections import OrderedDict
from xml.etree import ElementTree as ETree
from opcua import ua
from opcua import uamethod
from data_model_fboot import utils
import os
import sys
import logging


class UaMethod:

    def __init__(self, ua_server, ua_folder, xml_root):
        self.ua_server = ua_server
        self.ua_folder = ua_folder
        self.xml_root = xml_root

        self.fbs = dict()
        self.fbs_inputs = dict()
        self.fbs_outputs = dict()
        self.fb_connections = []
        
        self.inputs = OrderedDict()
        self.outputs = OrderedDict()

        # add inputs and outputs from fbt file
        starting_fb = self.ua_server.config.get_fb(self.ua_server.method_event.split('.')[0])
        self.get_fbs(starting_fb)
        self.add_inputs_outputs()

        # add event input
        arg = ua.Argument()
        arg.Name = self.ua_server.method_event
        arg.DataType = utils.UA_NODE[utils.UA_TYPES['String']]
        arg.ValueRank = 0
        # adds the argument to the list
        self.inputs[self.ua_server.method_event] = arg

        # create method on opc ua server
        self.virtualize()

    @uamethod
    def __execute(self, parent, *args):
        # set input values
        for i, (attr_name, _) in enumerate(self.inputs.items()):
            if attr_name != self.ua_server.method_event:
                chunks = attr_name.split('.') # fb_name.attr_name
                self.ua_server.config.fb_dictionary.get(chunks[0]).set_attr(chunks[1], args[i])

        # push event with user inserted value
        chunks = self.ua_server.method_event.split('.') # fb_name.event_name
        self.ua_server.config.fb_dictionary.get(chunks[0]).push_event(chunks[1], args[len(args) - 1])
        
        self.ua_server.config.fb_dictionary.get(self.ua_server.method_final_fb).execution_end.wait()

        output_return = []
        # read and save output values
        for i, (attr_name, _) in enumerate(self.outputs.items()):
            chunks = attr_name.split('.') # fb_name.attr_name
            _, value, _ = self.ua_server.config.fb_dictionary.get(chunks[0]).read_attr(chunks[1])
            output_return.append(value)

        if len(output_return) == 0:
            return None
        else:
            return tuple(output_return)

    def get_fbs(self, fb):
        self.fbs[fb.fb_name] = fb.fb_type
        if fb.fb_name == self.ua_server.method_final_fb:
            return
        for _, connections in fb.output_connections.items():
            for connection in connections:
                string_connection = connection.destination_fb.fb_name + '.' + connection.value_name
                if string_connection not in self.fb_connections:
                    self.fb_connections.append(string_connection)
                if connection.destination_fb.fb_name not in self.fbs:
                    self.get_fbs(connection.destination_fb)

    def add_inputs_outputs(self):

        has_inputs = False
        has_outputs = False

        if self.ua_server.method_inputs is not None:
            has_inputs = self.interpret_info(self.ua_server.method_inputs, self.fbs_inputs)

        if self.ua_server.method_outputs is not None:
            has_outputs = self.interpret_info(self.ua_server.method_outputs, self.fbs_outputs)

        for fb_name in self.fbs:
            file_name = self.fbs[fb_name] + '.fbt'
            root_path = utils.get_fb_files_path(self.fbs[fb_name])
            file_path = os.path.join(root_path, file_name)
            xml_tree = ETree.parse(file_path)
            xml_root = xml_tree.getroot()
            self.generate_inputs_outputs(fb_name, xml_root, has_inputs, has_outputs)

    def interpret_info(self, info, info_storage):
        info_string = info.replace(' ', '')
        info_string_list = ''

        for index in range(len(info_string)):
            if index == 0 or index == len(info_string) - 1:
                if info_string[index] not in '[]':
                    logging.warning('{0} is missing square brackets'.format(info))
                    return False
            else:
                info_string_list += info_string[index]

        info_array = info_string_list.split(',')

        for element in info_array:
            element_chunks = element.split('.') # FB_NAME.FB_VAR
            if len(element_chunks) != 2:
                logging.warning('Inputs/Outputs must be expressed in the following syntax: <FB_NAME.FB_PROPERTY>')
                return False
            if element_chunks[0] in info_storage:
                info_storage[element_chunks[0]].append(element_chunks[1]) 
            else:
                info_storage[element_chunks[0]] = [element_chunks[1]]

        return True

    def generate_inputs_outputs(self, fb_name, xml_root, inputs_defined, outputs_defined):
        for element in xml_root:
            for child in element:
                if child.tag == 'InputVars':
                    for var_declaration in child:
                        if 'OpcUa' in var_declaration.attrib:
                            # gets the name
                            var_name = var_declaration.attrib['Name']
                            # checks if it is not a part of the user defined inputs
                            if inputs_defined and (fb_name not in self.fbs_inputs or var_name not in self.fbs_inputs[fb_name]):
                                continue
                            # checks if input already receives value from connection
                            connection = fb_name + '.' + var_name
                            if connection in self.fb_connections:
                                continue
                            # checks if input already receives value from 4diac
                            _, value, _ = self.ua_server.config.get_fb(fb_name).read_attr(var_name)
                            if value is not None:
                                continue
                            # gets the type
                            var_type = var_declaration.attrib['Type']
                            # builds argument
                            arg = ua.Argument()
                            arg.Name = connection
                            arg.DataType = utils.UA_NODE[utils.UA_TYPES[var_type]]
                            arg.ValueRank = 0
                            # adds the argument to the list
                            self.inputs[connection] = arg
                if child.tag == 'OutputVars':
                    for var_declaration in child:
                        if 'OpcUa' in var_declaration.attrib:
                            # gets the name
                            var_name = var_declaration.attrib['Name']
                            # checks if it is a part of the user defined outputs
                            if outputs_defined and (fb_name not in self.fbs_outputs or var_name not in self.fbs_outputs[fb_name]):
                                continue
                            # gets the type
                            var_type = var_declaration.attrib['Type']
                            # builds argument
                            connection = fb_name + '.' + var_name
                            arg = ua.Argument()
                            arg.Name = connection
                            arg.DataType = utils.UA_NODE[utils.UA_TYPES[var_type]]
                            arg.ValueRank = 0
                            # adds the argument to the list                            
                            self.outputs[connection] = arg



    def virtualize(self):

        name = self.ua_server.opcua_method_name
        if name is None:
            name = self.xml_root.get('Name')

        # creates the opc-ua method
        method_idx = '{0}:{1}'.format(self.ua_folder.get('idx'), name)
        browse_name = '2:{0}'.format(name)
        self.ua_server.create_method(self.ua_folder.get('path'),
                                     method_idx,
                                     browse_name,
                                     self.__execute,
                                     input_args=list(self.inputs.values()),
                                     output_args=list(self.outputs.values()))


