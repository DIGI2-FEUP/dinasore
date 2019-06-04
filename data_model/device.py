from collections import OrderedDict
from data_model import utils
from opcua import ua


class Device(utils.DiacInterface):

    def __init__(self, ua_peer):
        utils.DiacInterface.__init__(self, ua_peer, 'DeviceSet')
        self.state = ''
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
        self.subs_id = root_xml.attrib['id']

        # creates the header opc-ua (description, ...) of this device
        self.__create_header(root_xml)

        # checks if exists that fb
        exist_fb = self.ua_peer.config.exists_fb(self.fb_name)
        # checks if the fb already exists
        if exist_fb is False:
            # creates the fb inside the configuration
            self.ua_peer.config.create_fb(self.fb_name, self.fb_type)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'variables':
                # link opc-ua variables in fb input variable
                self.__create_variables(item)

            elif tag == 'methods':
                # link opc-ua methods in fb methods
                self.__create_methods(item)

            elif tag == 'subscriptions':
                self.__create_context_links(item)

        # link variable to the start fb (sensor to init fb)
        if root_xml.attrib['type'] == 'SENSOR':
            self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                                  '{0}.{1}'.format(self.fb_name, 'Init'))

    def from_diac(self, fb):
        pass

    def __create_header(self, header_xml):
        # creates the device object
        for variables in header_xml:
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
                                self.create_base_object(self.fb_name)

                            # creates the fb
                            elif element.attrib['id'] == 'SourceType':
                                self.fb_type = element.text
                                # creates the respective property
                                utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                                                       property_name='SourceType', property_value=self.fb_type)

                            # creates the state
                            elif element.attrib['id'] == 'SourceState':
                                self.state = element.text
                                # creates the respective property
                                utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                                                       property_name='SourceState', property_value=self.state)
                        break
                break

            # create the id property
            utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', header_xml.attrib['id'])

    def __create_methods(self, methods_xml):
        # creates the methods folder
        folder_idx, methods_path = utils.default_folder(self.ua_peer,
                                                        self.base_idx, self.base_path, self.base_path_list,
                                                        'Methods')
        for method in methods_xml:
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

            # gets the created fb
            fb = self.ua_peer.config.get_fb(self.fb_name)

            method2call = Method2Call(method_name, fb,
                                      input_names, output_names,
                                      input_types, output_types)

            # creates the opc-ua method
            method_idx = '{0}:{1}'.format(folder_idx, method2call.method_name)
            browse_name = '2:{0}'.format(method2call.method_name)
            self.ua_peer.create_method(methods_path,
                                       method_idx,
                                       browse_name,
                                       method2call.execute,
                                       input_args=input_types,
                                       output_args=output_types)

    def __create_variables(self, vars_xml):
        # creates the variables folder
        folder_idx, vars_path = utils.default_folder(self.ua_peer,
                                                     self.base_idx, self.base_path, self.base_path_list,
                                                     'Variables')
        # creates the opc-ua variables and links them
        for var in vars_xml:
            if var.attrib['name'] != 'Description':
                var_name = var.attrib['name']
                # creates the opc-ua variable
                var_idx = '{0}:{1}'.format(folder_idx, var_name)
                browse_name = '2:{0}'.format(var_name)
                var_object = self.ua_peer.create_typed_variable(vars_path, var_idx, browse_name,
                                                                utils.UA_TYPES[var.attrib['DataType']],
                                                                utils.UA_RANKS[var.attrib['ValueRank']],
                                                                writable=False)
                # adds the variable to the dictionary
                self.__ua_variables[var_name] = var_object

    def __create_context_links(self, links_xml):
        # creates the subscriptions folder
        folder_idx, subscriptions_path = utils.default_folder(self.ua_peer,
                                                              self.base_idx, self.base_path,
                                                              self.base_path_list,
                                                              'Subscriptions')

        for subs in links_xml:
            # context connections between sensors/actuators and components/equipments
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
