from collections import OrderedDict
from data_model import utils
from opcua import ua


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
        device_list = None
        device_idx = 'ns=2;s={0}'.format(root_xml.attrib['id'])
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
                                self.fb_name = element.text
                                # creates the device object
                                device_list, device_path = utils.default_object(self.__ua_peer, device_idx,
                                                                                self.__DEVICE_SET_PATH,
                                                                                self.__DEVICE_SET_LIST,
                                                                                self.fb_name)
                            # creates the fb
                            elif element.attrib['id'] == 'SourceType':
                                self.fb_type = element.text
                                # creates the respective property
                                utils.default_property(self.__ua_peer, device_idx, device_path,
                                                       property_name='SourceType', property_value=self.fb_type)

                            # creates the state
                            elif element.attrib['id'] == 'SourceState':
                                self.state = element.text
                                # creates the respective property
                                utils.default_property(self.__ua_peer, device_idx, device_path,
                                                       property_name='SourceState', property_value=self.state)
                        break
                break

        # checks if exists that fb
        exist_fb = self.__ua_peer.config.exists_fb(self.fb_name)
        # checks if the fb already exists
        if exist_fb is False:
            # creates the fb inside the configuration
            self.__ua_peer.config.create_fb(self.fb_name, self.fb_type)
        # gets the created fb
        fb = self.__ua_peer.config.get_fb(self.fb_name)

        # create the id property
        utils.default_property(self.__ua_peer, device_idx, device_path, 'ID', root_xml.attrib['id'])

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # link opc-ua variables in fb input variable
            if tag == 'variables':
                # creates the variables folder
                folder_idx, vars_path = utils.default_folder(self.__ua_peer,
                                                             device_idx, device_path, device_list,
                                                             'Variables')
                # creates the opc-ua variables and links them
                for var in item:
                    if var.attrib['name'] != 'Description':
                        var_name = var.attrib['name']
                        # creates the opc-ua variable
                        var_idx = '{0}:{1}'.format(folder_idx, var_name)
                        browse_name = '2:{0}'.format(var_name)
                        var_object = self.__ua_peer.create_typed_variable(vars_path, var_idx, browse_name,
                                                                          utils.UA_TYPES[var.attrib['DataType']],
                                                                          utils.UA_RANKS[var.attrib['ValueRank']],
                                                                          writable=False)
                        # adds the variable to the dictionary
                        self.__ua_variables[var_name] = var_object

            # link opc-ua methods in fb methods
            elif tag == 'methods':
                # creates the methods folder
                folder_idx, methods_path = utils.default_folder(self.__ua_peer,
                                                                device_idx, device_path, device_list,
                                                                'Methods')
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
                            output_types.append(utils.UA_TYPES[arg_type])
                        elif argument.attrib['type'] == 'Input':
                            # gets the name
                            input_names.append(argument.attrib['name'])
                            # gets the type
                            arg_type = argument.attrib['DataType']
                            input_types.append(utils.UA_TYPES[arg_type])

                    method2call = Method2Call(method_name, fb,
                                              input_names, output_names,
                                              input_types, output_types)

                    # creates the opc-ua method
                    method_idx = '{0}:{1}'.format(folder_idx, method2call.method_name)
                    browse_name = '2:{0}'.format(method2call.method_name)
                    self.__ua_peer.create_method(methods_path,
                                                 method_idx,
                                                 browse_name,
                                                 method2call.execute,
                                                 input_args=input_types,
                                                 output_args=output_types)

            elif tag == 'subscriptions':
                # creates the subscriptions folder
                folder_idx, subscriptions_path = utils.default_folder(self.__ua_peer,
                                                                      device_idx, device_path, device_list,
                                                                      'Subscriptions')

                for subs in item:
                    # context connections between sensors/actuators and components/equipments
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
