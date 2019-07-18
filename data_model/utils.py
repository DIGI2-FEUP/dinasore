from opcua import ua
from opcua import uamethod
import uuid
import xml.etree.ElementTree as ETree
from collections import OrderedDict

UA_TYPES = {'String': ua.VariantType.String,
            'STRING': ua.VariantType.String,
            'Double': ua.VariantType.Double,
            'Integer': ua.VariantType.Int64,
            'INT': ua.VariantType.Int64,
            'UINT': ua.VariantType.UInt64,
            'Float': ua.VariantType.Float,
            'REAL': ua.VariantType.Float,
            'LREAL': ua.VariantType.Float,
            'BOOL': ua.VariantType.Boolean,
            'Boolean': ua.VariantType.Boolean}

XML_4DIAC = {'String': 'String',
             'STRING': 'String',
             'Double': 'Double',
             'Integer': 'Integer',
             'INT': 'Integer',
             'UINT': 'Integer',
             'Float': 'Float',
             'REAL': 'Float',
             'LREAL': 'Float',
             'BOOL': 'Boolean',
             'Boolean': 'Boolean'}

UA_NODE = {ua.VariantType.String: ua.NodeId(ua.ObjectIds.String),
           ua.VariantType.Double: ua.NodeId(ua.ObjectIds.Double),
           ua.VariantType.Int64: ua.NodeId(ua.ObjectIds.Int64),
           ua.VariantType.UInt64: ua.NodeId(ua.ObjectIds.UInt64),
           ua.VariantType.Float: ua.NodeId(ua.ObjectIds.Float),
           ua.VariantType.Boolean: ua.NodeId(ua.ObjectIds.Boolean)}

XML_TYPES = {ua.VariantType.String: 'String',
             ua.VariantType.Double: 'Double',
             ua.VariantType.Int64: 'Integer',
             ua.VariantType.UInt64: 'Integer',
             ua.VariantType.Float: 'Float',
             ua.VariantType.Boolean: 'Boolean'}

XML_NODE = {ua.ObjectIds.String: 'String',
            ua.ObjectIds.Double: 'Double',
            ua.ObjectIds.Int64: 'Integer',
            ua.ObjectIds.UInt64: 'Integer',
            ua.ObjectIds.Float: 'Float',
            ua.ObjectIds.Boolean: 'Boolean'}


def default_folder(ua_peer, obj_idx, obj_path, path_list, folder_name):
    # creates the methods folder
    folder_idx = '{0}:{1}'.format(obj_idx, folder_name)
    browse_name = '2:{0}'.format(folder_name)
    ua_peer.create_folder(obj_path, folder_idx, browse_name)
    # path for the methods folder
    folder_list = path_list + [(2, folder_name)]
    folder_path = ua_peer.generate_path(folder_list)
    return folder_idx, folder_path, folder_list


def default_property(ua_peer, obj_idx, obj_path, property_name, property_value):
    prop_idx = '{0}.{1}'.format(obj_idx, property_name)
    browse_name = '2:{0}'.format(property_name)
    ua_peer.create_property(obj_path, prop_idx, browse_name, property_value)


def default_object(ua_peer, obj_idx, obj_path, path_list, obj_name):
    browse_name = '2:{0}'.format(obj_name)
    ua_peer.create_object(obj_idx, browse_name, path=obj_path)
    # sets the path for the device object
    new_list = path_list + [(2, obj_name)]
    new_path = ua_peer.generate_path(new_list)
    return new_list, new_path


def parse_fb_description(fb_xml):
    fb_id, ua_type = None, None
    input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = None, None, None, None
    for item in fb_xml:
        # gets the id
        if item.tag == 'SelfDescription':
            fb_id = item.attrib['ID']
            ua_type = item.attrib['FBType']
        # gets the events and vars
        elif item.tag == 'InterfaceList':
            # Iterates over the interface list
            # to find the inputs/outputs
            for interface in item:
                # Input events
                if interface.tag == 'EventInputs':
                    input_events_xml = interface
                # Output events
                elif interface.tag == 'EventOutput':
                    output_events_xml = interface
                # Input variables
                elif interface.tag == 'InputVars':
                    input_vars_xml = interface
                # Output variables
                elif interface.tag == 'OutputVars':
                    output_vars_xml = interface

    return fb_id, ua_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml


class UaInterface:

    def from_xml(self, item_xml):
        raise NotImplementedError

    def from_fb(self, fb, optional_fb_xml):
        raise NotImplementedError

    def save_xml(self, xml_set):
        raise NotImplementedError


class UaBaseStructure:

    def __init__(self, ua_peer, folder_name, subs_id, fb_name, fb_type, browse_name):
        self.subs_id = subs_id
        self.fb_name = fb_name
        self.fb_type = fb_type
        self.ua_peer = ua_peer
        self.folder_name = folder_name
        self.ua_variables = dict()

        # creates the path to set the folder
        folder_path_list = self.ua_peer.ROOT_LIST + [(2, self.folder_name)]
        folder_path = self.ua_peer.generate_path(folder_path_list)

        self.base_idx = 'ns=2;s={0}'.format(self.subs_id)
        # creates the device object
        self.base_path_list, self.base_path = default_object(self.ua_peer, self.base_idx,
                                                             folder_path, folder_path_list,
                                                             browse_name)

        # creates the methods folder
        self.methods_idx, self.methods_path, methods_list = default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                           self.base_path_list, 'Methods')

        # creates the variables folder
        self.vars_idx, self.vars_path, self.vars_list = default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                       self.base_path_list, 'Variables')
        # key: constant_name, value: value to set (converted)
        self.variables_list = []

        # creates the subscriptions folder
        subs_idx, subs_path, subs_list = default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                        self.base_path_list, 'Subscriptions')
        self.subscriptions_folder = self.ua_peer.get_object(subs_path)
        # creates the dictionary where are stored teh connections
        self.subscriptions_dict = dict()

    def virtualize_xml_variable(self, var_xml):
        var_name = var_xml.attrib['name']
        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(self.vars_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # convert array dimensions
        array_dimensions = 0
        if 'ArrayDimensions' in var_xml.attrib:
            array_dimensions = int(var_xml.attrib['ArrayDimensions'])
        var_object = self.ua_peer.create_typed_variable(self.vars_path, var_idx, browse_name,
                                                        UA_TYPES[var_xml.attrib['DataType']],
                                                        int(var_xml.attrib['ValueRank']),
                                                        dimensions=array_dimensions,
                                                        writable=False)
        var_path = self.ua_peer.generate_path(self.vars_list + [(2, var_name)])
        return var_idx, var_object, var_path

    def virtualize_fb_variable(self, var_xml):
        var_name = var_xml.attrib['Name']
        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(self.vars_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # CHECK THE VALUE RANK OF THE VARIABLE
        var_object = self.ua_peer.create_typed_variable(self.vars_path, var_idx, browse_name,
                                                        UA_TYPES[var_xml.attrib['Type']],
                                                        0,
                                                        writable=False)
        var_path = self.ua_peer.generate_path(self.vars_list + [(2, var_name)])
        return var_idx, var_object, var_path

    def virtualize_dict_variable(self, var_dict):
        var_name = var_dict['Name']
        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(self.vars_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # convert array dimensions
        array_dimensions = 0
        if 'ArrayDimensions' in var_dict:
            array_dimensions = int(var_dict['ArrayDimensions'])
        var_object = self.ua_peer.create_typed_variable(self.vars_path, var_idx, browse_name,
                                                        UA_TYPES[var_dict['DataType']],
                                                        int(var_dict['ValueRank']),
                                                        dimensions=array_dimensions,
                                                        writable=False)
        var_path = self.ua_peer.generate_path(self.vars_list + [(2, var_name)])
        return var_idx, var_object, var_path

    def create_dict_variable_xml(self, var_xml, var_type):
        var_dict = dict()
        var_dict['Name'] = var_xml.attrib['name']
        var_dict['DataType'] = var_xml.attrib['DataType']
        var_dict['ValueRank'] = var_xml.attrib['ValueRank']
        var_dict['Type'] = var_type
        # adds the variable to the dict
        self.variables_list.append(var_dict)

    def create_dict_variable_fb(self, var_type, var_xml):
        if var_xml.attrib['OpcUa'] == 'Variable':
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': var_type,
                        'DataType': XML_4DIAC[var_xml.attrib['Type']],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)
        elif var_xml.attrib['OpcUa'] == 'Constant':
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': 'Constant',
                        'DataType': XML_4DIAC[var_xml.attrib['Type']],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)

    def create_ua_connection(self, source_node, destination_variable):
        # adds that subscription to the folder
        var_ref = self.ua_peer.get_node('ns=2;s={0}'.format(source_node))
        self.subscriptions_folder.add_reference(var_ref, ua.ObjectIds.Organizes)
        # saves the subscription in the dictionary
        self.subscriptions_dict[destination_variable] = var_ref

    def parse_subscriptions(self, links_xml):
        from data_model import device
        from data_model import instance
        from data_model import point

        # iterates over each subscription of the set
        for subscription in links_xml:

            # checks if is context subscription
            if subscription.attrib['type'] == 'Context':
                pass
            # checks if is data subscription
            elif subscription.attrib['type'] == 'Data':
                # its an input variable
                if subscription.attrib['BrowseDirection'] == 'forward':
                    # parses the subscription
                    sub_splitted = subscription.text.split(':')
                    # gets the destination fb
                    content = self.ua_peer.search_id(sub_splitted[0])
                    # creates the connection between the fb
                    source = '{0}.{1}'.format(content.fb_name, sub_splitted[2])
                    destination = '{0}.{1}'.format(self.subs_id, subscription.attrib['VariableName'])
                    self.ua_peer.config.create_connection(source=source, destination=destination)
                    # connect the output event to input event
                    if isinstance(content, device.Device) or isinstance(content, point.Point):
                        source_event = '{0}.{1}'.format(content.fb_name, 'READ_O')
                    elif isinstance(content, instance.InstanceService):
                        source_event = '{0}.{1}'.format(content.fb_name, 'RUN_O')
                    else:
                        source_event = '{0}.{1}'.format(content.fb_name, 'RUN_O')

                    # creates the connection between the fb
                    destination_event = '{0}.{1}'.format(self.subs_id, 'RUN')
                    self.ua_peer.config.create_connection(source=source_event, destination=destination_event)

                    # adds that subscription to the folder
                    var_ref = self.ua_peer.get_node('ns=2;s={0}'.format(subscription.text))
                    self.subscriptions_folder.add_reference(var_ref, ua.ObjectIds.Organizes)
                    # saves the subscription in the dictionary
                    self.subscriptions_dict[subscription.attrib['VariableName']] = var_ref

                # its a constant
                elif subscription.attrib['BrowseDirection'] == 'both':
                    # gets the value to write
                    source = subscription.text
                    destination = '{0}.{1}'.format(self.subs_id, subscription.attrib['VariableName'])
                    # write the value in the fb
                    self.ua_peer.config.write_connection(source_value=source, destination=destination)
                    # case is one of this classes
                    if isinstance(self, device.Device) or isinstance(self, point.Point):
                        # add the variable to the constant list
                        self.variables_list.append({'Name': subscription.attrib['VariableName'], 'Type': 'Constant'})

                # its an output variable
                elif subscription.attrib['BrowseDirection'] == 'inverse':
                    pass

    def create_extras(self):
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))
        # creates the fb that runs the device in loop
        sleep_fb_name = str(uuid.uuid4())
        self.ua_peer.config.create_fb(sleep_fb_name, 'SLEEP')
        self.ua_peer.config.create_connection('{0}.{1}'.format(self.fb_name, 'INIT_O'),
                                              '{0}.{1}'.format(sleep_fb_name, 'SLEEP'))
        self.ua_peer.config.create_connection('{0}.{1}'.format(sleep_fb_name, 'SLEEP_O'),
                                              '{0}.{1}'.format(self.fb_name, 'READ'))
        self.ua_peer.config.create_connection('{0}.{1}'.format(self.fb_name, 'READ_O'),
                                              '{0}.{1}'.format(sleep_fb_name, 'SLEEP'))

    def update_variables(self):
        # gets the function block
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # iterates over the variables dict
        for var_name, var_ua in self.ua_variables.items():
            # reads the variable value
            v_type, value, is_watch = fb.read_attr(var_name)
            # writes the value inside the opc-ua variable
            var_ua.set_value(value)


class Method2Call(UaInterface):

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
                arg.DataType = UA_NODE[UA_TYPES[argument.attrib['DataType']]]
                arg.ValueRank = int(argument.attrib['ValueRank'])
                # adds the argument to the list
                self.outputs[var_name] = arg
            elif argument.attrib['type'] == 'Input':
                # gets the name
                var_name = argument.attrib['name']
                # gets the type
                arg = ua.Argument()
                arg.Name = argument.attrib['name']
                arg.DataType = UA_NODE[UA_TYPES[argument.attrib['DataType']]]
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
                    arg.DataType = UA_NODE[UA_TYPES[entry.attrib['Type']]]
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
                    arg.DataType = UA_NODE[UA_TYPES[entry.attrib['Type']]]
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
            arg_xml.attrib['DataType'] = XML_NODE[input_arg.DataType.Identifier]
            arg_xml.attrib['ValueRank'] = str(input_arg.ValueRank)
        # get the output arguments
        for output_name, output_arg in self.outputs.items():
            # creates the xml argument
            arg_xml = ETree.SubElement(method_arguments, 'argument')
            arg_xml.attrib['name'] = output_arg.Name
            arg_xml.attrib['type'] = 'Output'
            arg_xml.attrib['DataType'] = XML_NODE[output_arg.DataType.Identifier]
            arg_xml.attrib['ValueRank'] = str(output_arg.ValueRank)

    def parse_variable(self, var_dict):
        # gets the name
        var_name = var_dict['Name']
        # gets the type
        arg = ua.Argument()
        arg.Name = var_dict['Name']
        arg.DataType = UA_NODE[UA_TYPES[var_dict['DataType']]]
        arg.ValueRank = int(var_dict['ValueRank'])
        # sets a input or output variable
        if var_dict['Type'] == 'Input':
            self.inputs[var_name] = arg
        elif var_dict['Type'] == 'Output':
            self.outputs[var_name] = arg

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
