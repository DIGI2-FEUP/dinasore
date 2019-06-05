from opcua import ua
from collections import OrderedDict

UA_TYPES = {'String': ua.VariantType.String,
            'Double': ua.VariantType.Double,
            'Integer': ua.VariantType.Int64,
            'Float': ua.VariantType.Float,
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


class UaBaseStructure:

    def __init__(self, ua_peer, folder_name):
        self.fb_name, self.fb_type = None, None
        self.subs_id = None
        self.base_idx, self.base_path, self.base_path_list = None, None, None
        self.ua_peer = ua_peer
        self.folder_name = folder_name

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


class DiacInterface(UaBaseStructure):

    def __init__(self, ua_peer, folder_name):
        UaBaseStructure.__init__(self, ua_peer, folder_name)
        self.ua_variables = dict()

    def __create_methods(self, methods_xml):
        raise NotImplementedError

    def __create_variables(self, variables_xml):
        raise NotImplementedError

    def __create_header(self, header_xml):
        raise NotImplementedError

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
        self.input_types = []
        self.output_types = []

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
                self.outputs[var_name] = arg_type
                self.output_types.append(UA_TYPES[arg_type])
            elif argument.attrib['type'] == 'Input':
                # gets the name
                var_name = argument.attrib['name']
                # gets the type
                arg_type = argument.attrib['DataType']
                self.inputs[var_name] = arg_type
                self.input_types.append(UA_TYPES[arg_type])

    def virtualize(self, folder_idx, methods_path):
        # creates the opc-ua method
        method_idx = '{0}:{1}'.format(folder_idx, self.method_name)
        browse_name = '2:{0}'.format(self.method_name)
        self.__ua_peer.create_method(methods_path,
                                     method_idx,
                                     browse_name,
                                     self.execute,
                                     input_args=self.input_types,
                                     output_args=self.output_types)
