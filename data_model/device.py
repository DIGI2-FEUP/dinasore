from collections import OrderedDict
from core import fb_resources
from opcua import ua

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


class DeviceSet:

    def __init__(self, ua_peer):
        self.__devices = dict()
        # receives the peer methods to add the opc-ua objects
        self.__ua_peer = ua_peer

        # creates the opc-ua folder
        idx = 'ns=2;s={0}:{1}'.format(self.__ua_peer.idx, 'DeviceSet')
        self.__ua_peer.create_folder(self.__ua_peer.ROOT_PATH, idx, '2:DeviceSet')

    def from_xml(self, xml_set):
        for dev_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = dev_xml.tag[1:].partition("}")

            if tag == 'device':
                dev = Device(self.__ua_peer)
                dev.from_xml(dev_xml)

                # use the fb_name as key
                self.__devices[dev.fb_name] = dev

    def from_diac(self, fb_type, fb):
        # get the xml fb definition xml file
        fb = fb_resources.FBResources(fb_type)

        # gets the device id and type
        dev_id, dev_type = fb.get_description()
        # creates the device
        dev = Device(self.__ua_peer)
        # links the fb to the device
        dev.from_diac(fb)

        # adds the device to the dictionary
        self.__devices[dev_id] = dev


class Device:

    def __init__(self, ua_peer):
        self.fb_name, self.fb_type, self.state = '', '', ''
        self.__ua_peer = ua_peer

        # creates the path to that folder
        self.__DEVICE_SET_LIST = self.__ua_peer.ROOT_LIST + [(2, 'DeviceSet')]
        self.__DEVICE_SET_PATH = self.__ua_peer.generate_path(self.__DEVICE_SET_LIST)

        self.__ua_variables = dict()

    def from_xml(self, root_xml):
        """
        device               -> fb
            description.name -> fb_type
        methods              -> input_events
        data_vars            -> output_vars
            variable.name    -> output_var_name

        :param root_xml:
        """
        device_path = ''
        device_type = root_xml.attrib['type']

        # creates the device object
        for variables in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = variables.tag[1:].partition("}")

            if tag == 'variables':
                for var in variables:
                    if var.attrib['name'] == 'Description':
                        # creates the device properties
                        for element in var[0]:
                            # creates the opc-ua object
                            if element.attrib['id'] == 'Name':
                                # creates the device object
                                self.fb_name = element.text
                                self.__ua_peer.create_object(2, self.fb_name, path=self.__DEVICE_SET_PATH)
                                # sets the path for the device object
                                device_path = self.__ua_peer.generate_path(self.__DEVICE_SET_LIST +
                                                                           [(2, self.fb_name)])
                            # creates the fb
                            elif element.attrib['id'] == 'SourceType':
                                self.fb_type = element.text
                                # creates the respective property
                                self.__ua_peer.create_property(device_path, 2, 'SourceType', self.fb_type)

                            #
                            elif element.attrib['id'] == 'SourceState':
                                self.state = element.text
                                # creates the respective property
                                self.__ua_peer.create_property(device_path, 2, 'SourceState', self.state)
                        break
                break

        # gets the created fb
        fb = self.__ua_peer.config.get_fb(self.fb_name)
        # checks if the fb already exists
        if fb is None:
            # creates the fb inside the configuration
            self.__ua_peer.config.create_fb(self.fb_name, self.fb_type)
            fb = self.__ua_peer.config.get_fb(self.fb_name)

        # create the id property
        self.__ua_peer.create_property(device_path, 2, 'ID', root_xml.attrib['id'])

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # link opc-ua variables in fb input variable
            if tag == 'variables':
                # creates the variables folder
                self.__ua_peer.create_folder(device_path, 2, 'Variables')
                # path for the variables folder
                vars_path = self.__ua_peer.generate_path(self.__DEVICE_SET_LIST +
                                                         [(2, self.fb_name), (2, 'Variables')])
                # creates the opc-ua variables and links them
                for var in item:
                    if var.attrib['name'] != 'Description':
                        var_name = var.attrib['name']
                        # creates the opc-ua variable
                        var_object = self.__ua_peer.create_typed_variable(vars_path,
                                                                          2,
                                                                          var_name,
                                                                          UA_TYPES[var.attrib['DataType']],
                                                                          UA_RANKS[var.attrib['ValueRank']],
                                                                          writable=False)
                        # adds the variable to the dictionary
                        self.__ua_variables[var_name] = var_object

            # link opc-ua methods in fb methods
            elif tag == 'methods':
                # creates the variables folder
                self.__ua_peer.create_folder(device_path, 2, 'Methods')
                # path for the variables folder
                methods_path = self.__ua_peer.generate_path(self.__DEVICE_SET_LIST +
                                                            [(2, self.fb_name), (2, 'Methods')])

                for method in item:
                    method_name = method.attrib['name']

                    input_types, output_types = [], []
                    input_names, output_names = [], []
                    # first parse the inputs and the outputs
                    for argument in method[0]:
                        if argument.attrib['type'] == 'Output':
                            # gets the name
                            output_names.append(argument.attrib['name'])
                            # gets the type
                            arg_type = argument.attrib['DataType']
                            output_types.append(UA_TYPES[arg_type])
                        elif argument.attrib['type'] == 'Input':
                            # gets the name
                            input_names.append(argument.attrib['name'])
                            # gets the type
                            arg_type = argument.attrib['DataType']
                            input_types.append(UA_TYPES[arg_type])

                    method2call = Method2Call(method_name, fb,
                                              input_names, output_names,
                                              input_types, output_types)

                    # creates the opc-ua method
                    self.__ua_peer.create_method(methods_path,
                                                 2,
                                                 method2call.method_name,
                                                 method2call.execute,
                                                 input_args=input_types,
                                                 output_args=output_types)

            elif tag == 'subscriptions':
                for subs in item:
                    pass

        # link variable to the start fb (sensor to init fb)
        if device_type == 'SENSOR':
            self.__ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                                    '{0}.{1}'.format(self.fb_name, 'Init'))

    def from_diac(self, fb):
        pass


class Method2Call:
    def __init__(self, method_name, fb, input_names, output_names, input_types, output_types):
        self.method_name = method_name
        self.fb = fb

        self.inputs = OrderedDict()
        for i in range(len(input_types)):
            self.inputs[input_names[i]] = input_types[i]

        self.outputs = OrderedDict()
        for i in range(len(output_types)):
            self.outputs[output_names[i]] = output_types[i]

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
