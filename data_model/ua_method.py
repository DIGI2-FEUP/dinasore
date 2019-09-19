from opcua import ua
from opcua import uamethod
from collections import OrderedDict
import xml.etree.ElementTree as ETree
from data_model import utils


class Method2Call(utils.UaInterface):

    def __init__(self, method_name, fb, ua_peer):
        self.method_name = method_name
        self.fb = fb
        self.__ua_peer = ua_peer

        self.inputs = OrderedDict()
        self.outputs = OrderedDict()

    @uamethod
    def __execute(self, parent, *args):
        for i, (input_name, input_type) in enumerate(self.inputs.items()):
            self.fb.set_attr(input_name, args[i])

        self.fb.push_event(self.method_name, 10)

        self.fb.execution_end.wait()

        output_return = []
        for i, (output_name, output_type) in enumerate(self.outputs.items()):
            v_type, value, is_watch = self.fb.read_attr(output_name)
            output_return.append(value)

        if len(output_return) == 0:
            return None
        else:
            return output_return

    def from_xml(self, method_xml):
        # first parse the inputs and the outputs
        for argument in method_xml[0]:
            if argument.attrib['type'] == 'Output':
                # gets the name
                var_name = argument.attrib['name']
                # gets the type
                arg = ua.Argument()
                arg.Name = argument.attrib['name']
                arg.DataType = utils.UA_NODE[utils.UA_TYPES[argument.attrib['DataType']]]
                arg.ValueRank = int(argument.attrib['ValueRank'])
                # adds the argument to the list
                self.outputs[var_name] = arg
            elif argument.attrib['type'] == 'Input':
                # gets the name
                var_name = argument.attrib['name']
                # gets the type
                arg = ua.Argument()
                arg.Name = argument.attrib['name']
                arg.DataType = utils.UA_NODE[utils.UA_TYPES[argument.attrib['DataType']]]
                arg.ValueRank = int(argument.attrib['ValueRank'])
                # adds the argument to the list
                self.inputs[var_name] = arg

    def from_fb(self, input_xml, output_xml):
        # gets the method input arguments
        for entry in input_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if self.method_name in var_specs:
                    # gets the name
                    var_name = entry.attrib['Name']
                    # gets the type
                    arg = ua.Argument()
                    arg.Name = entry.attrib['Name']
                    arg.DataType = utils.UA_NODE[utils.UA_TYPES[entry.attrib['Type']]]
                    arg.ValueRank = 0
                    # adds the argument to the list
                    self.inputs[var_name] = arg
        # gets the method output arguments
        for entry in output_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if self.method_name in var_specs:
                    # gets the name
                    var_name = entry.attrib['Name']
                    # gets the type
                    arg = ua.Argument()
                    arg.Name = entry.attrib['Name']
                    arg.DataType = utils.UA_NODE[utils.UA_TYPES[entry.attrib['Type']]]
                    arg.ValueRank = 0
                    # adds the argument to the list
                    self.outputs[var_name] = arg

    def save_xml(self, method_xml):
        # writes the method name
        method_xml.attrib['name'] = self.method_name

        # creates the arguments tag
        method_arguments = ETree.SubElement(method_xml, 'arguments')
        # get the input arguments
        for input_name, input_arg in self.inputs.items():
            # creates the xml argument
            arg_xml = ETree.SubElement(method_arguments, 'argument')
            arg_xml.attrib['name'] = input_arg.Name
            arg_xml.attrib['type'] = 'Input'
            arg_xml.attrib['DataType'] = utils.XML_NODE[input_arg.DataType.Identifier]
            arg_xml.attrib['ValueRank'] = str(input_arg.ValueRank)
        # get the output arguments
        for output_name, output_arg in self.outputs.items():
            # creates the xml argument
            arg_xml = ETree.SubElement(method_arguments, 'argument')
            arg_xml.attrib['name'] = output_arg.Name
            arg_xml.attrib['type'] = 'Output'
            arg_xml.attrib['DataType'] = utils.XML_NODE[output_arg.DataType.Identifier]
            arg_xml.attrib['ValueRank'] = str(output_arg.ValueRank)

    def virtualize(self, folder_idx, methods_path, ua_name):
        # creates the opc-ua method
        method_idx = '{0}:{1}'.format(folder_idx, ua_name)
        browse_name = '2:{0}'.format(ua_name)
        self.__ua_peer.create_method(methods_path,
                                     method_idx,
                                     browse_name,
                                     self.__execute,
                                     input_args=list(self.inputs.values()),
                                     output_args=list(self.outputs.values()))
