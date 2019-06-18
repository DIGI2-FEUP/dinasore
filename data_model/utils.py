from opcua import ua
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

UA_RANKS = {'1': ua.ValueRank.OneDimension,
            '0': ua.ValueRank.OneOrMoreDimensions,
            '-1': ua.ValueRank.Scalar,
            '-2': ua.ValueRank.Any,
            '-3': ua.ValueRank.ScalarOrOneDimension}


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


def read_description_from_fb(fb_xml):
    search_id, search_type = None, None
    # gets the search_id
    for entry in fb_xml:
        # splits the tag in these 3 camps
        uri, ignore, tag = fb_xml.tag[1:].partition("}")
        if tag == 'SelfDiscription':
            search_id = entry.attrib['ID']
            search_type = entry.attrib['FBType']
    return search_id, search_type


class UaBaseStructure:

    def __init__(self, ua_peer, folder_name):
        self.fb_name, self.fb_type = None, None
        self.subs_id = None
        self.base_idx, self.base_path, self.base_path_list = None, None, None
        self.ua_peer = ua_peer
        self.folder_name = folder_name
        self.ua_variables = dict()

    def from_xml(self, root_xml):
        raise NotImplementedError

    def create_base_object(self, browse_name):
        # creates the path to set the folder
        folder_path_list = self.ua_peer.ROOT_LIST + [(2, self.folder_name)]
        folder_path = self.ua_peer.generate_path(folder_path_list)

        self.base_idx = 'ns=2;s={0}'.format(self.subs_id)
        # creates the device object
        self.base_path_list, self.base_path = default_object(self.ua_peer, self.base_idx,
                                                             folder_path, folder_path_list,
                                                             browse_name)

    def create_variable(self, var_xml, folder_idx, vars_path):
        var_name = var_xml.attrib['name']
        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(folder_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # convert array dimensions
        array_dimensions = 0
        if 'ArrayDimensions' in var_xml.attrib:
            array_dimensions = int(var_xml.attrib['ArrayDimensions'])
        var_object = self.ua_peer.create_typed_variable(vars_path, var_idx, browse_name,
                                                        UA_TYPES[var_xml.attrib['DataType']],
                                                        UA_RANKS[var_xml.attrib['ValueRank']],
                                                        dimensions=array_dimensions,
                                                        writable=False)
        return var_idx, var_object

    def create_variable_by_dict(self, var_dict, folder_idx, vars_path):
        var_name = var_dict['Name']
        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(folder_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # convert array dimensions
        array_dimensions = 0
        if 'ArrayDimensions' in var_dict:
            array_dimensions = int(var_dict['ArrayDimensions'])
        var_object = self.ua_peer.create_typed_variable(vars_path, var_idx, browse_name,
                                                        UA_TYPES[var_dict['DataType']],
                                                        UA_RANKS[var_dict['ValueRank']],
                                                        dimensions=array_dimensions,
                                                        writable=False)
        return var_idx, var_object

    def create_fb_variable(self, var_xml, folder_idx, vars_path):
        var_name = var_xml.attrib['Name']
        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(folder_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # CHECK THE VALUE RANK OF THE VARIABLE
        var_object = self.ua_peer.create_typed_variable(vars_path, var_idx, browse_name,
                                                        UA_TYPES[var_xml.attrib['Type']],
                                                        UA_RANKS['0'],
                                                        writable=False)
        return var_idx, var_object

    def parse_fb_description(self, fb_xml):
        ua_type = None
        input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = None, None, None, None
        for item in fb_xml:
            # gets the id
            if item.tag == 'SelfDiscription':
                self.subs_id = item.attrib['ID']
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

        return ua_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml

    def update_variables(self):
        # gets the function block
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # iterates over the variables dict
        for var_name, var_ua in self.ua_variables.items():
            # reads the variable value
            v_type, value, is_watch = fb.read_attr(var_name)
            # writes the value inside the opc-ua variable
            var_ua.set_value(value)


class Method2Call:

    def __init__(self, method_name, fb, ua_peer):
        self.method_name = method_name
        self.fb = fb
        self.__ua_peer = ua_peer

        self.inputs = OrderedDict()
        self.outputs = OrderedDict()

    def execute(self, parent, *args):
        for i, (input_name, input_type) in enumerate(self.inputs.items()):
            self.fb.set_attr(input_name, args[i].Value)

        self.fb.push_event(self.method_name, 10)

        self.fb.execution_end.wait()

        output_return = []
        for i, (output_name, output_type) in enumerate(self.outputs.items()):
            v_type, value, is_watch = self.fb.read_attr(output_name)
            output_return.append(ua.Variant(value, output_type))

        return output_return

    def from_xml(self, method_xml):
        # first parse the inputs and the outputs
        for argument in method_xml[0]:
            if argument.attrib['type'] == 'Output':
                # gets the name
                var_name = argument.attrib['name']
                # gets the type
                arg_type = argument.attrib['DataType']
                self.outputs[var_name] = UA_TYPES[arg_type]
            elif argument.attrib['type'] == 'Input':
                # gets the name
                var_name = argument.attrib['name']
                # gets the type
                arg_type = argument.attrib['DataType']
                self.inputs[var_name] = UA_TYPES[arg_type]

    def from_fb(self, input_xml, output_xml):
        # gets the method input arguments
        for entry in input_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if self.method_name in var_specs:
                    # gets the name
                    var_name = entry.attrib['Name']
                    # gets the type
                    arg_type = entry.attrib['Type']
                    self.inputs[var_name] = UA_TYPES[arg_type]

        # gets the method output arguments
        for entry in output_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if self.method_name in var_specs:
                    # gets the name
                    var_name = entry.attrib['Name']
                    # gets the type
                    arg_type = entry.attrib['Type']
                    self.outputs[var_name] = UA_TYPES[arg_type]

    def parse_variable(self, var_dict):
        # gets the name
        var_name = var_dict['Name']
        # gets the type
        arg_type = var_dict['DataType']
        # sets a input or output variable
        if var_dict['Type'] == 'Input':
            self.inputs[var_name] = UA_TYPES[arg_type]
        if var_dict['Type'] == 'Output':
            self.outputs[var_name] = UA_TYPES[arg_type]

    def virtualize(self, folder_idx, methods_path, ua_name):
        # creates the opc-ua method
        method_idx = '{0}:{1}'.format(folder_idx, ua_name)
        browse_name = '2:{0}'.format(ua_name)
        self.__ua_peer.create_method(methods_path,
                                     method_idx,
                                     browse_name,
                                     self.execute,
                                     input_args=list(self.inputs.values()),
                                     output_args=list(self.outputs.values()))
