from data_model import utils


class Device(utils.DiacInterface):

    def __init__(self, ua_peer):
        utils.DiacInterface.__init__(self, ua_peer, 'DeviceSet')
        self.state = ''

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
        self.__parse_header(root_xml)

        # creates the fb inside the configuration
        self.ua_peer.config.create_virtualized_fb(self.fb_name, self.fb_type, self.update_variables)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'variables':
                # link opc-ua variables in fb input variable
                self.__parse_variables(item)

            elif tag == 'methods':
                # link opc-ua methods in fb methods
                self.__parse_methods(item)

            elif tag == 'subscriptions':
                self.__create_context_links(item)

        # link variable to the start fb (sensor to init fb)
        if root_xml.attrib['type'] == 'SENSOR':
            self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                                  '{0}.{1}'.format(self.fb_name, 'Init'))

    def from_fb(self, fb, fb_xml):
        # gets the fb_name
        self.fb_name = fb.fb_name
        # gets the fb_type
        self.fb_type = fb.fb_type
        # updates the state
        self.state = 'RUNNING'
        input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = None, None, None, None
        for item in fb_xml:
            # gets the id
            if item.tag == 'SelfDiscription':
                self.subs_id = item.attrib['ID']
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

        # creates the header opc-ua items
        self.__create_header_objects()

        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                      self.base_path,
                                                                      self.base_path_list, 'Methods')
        # Iterates over the input events
        for event in input_events_xml:
            # check if is a opc-ua method
            if 'OpcUa' in event.attrib:
                if event.attrib['OpcUa'] == 'Method':
                    # gets the method name
                    method_name = event.attrib['Name']
                    # creates the opc-ua method
                    method2call = utils.Method2Call(method_name, fb, self.ua_peer)
                    # parses the inputs_vars and the output_vars
                    method2call.from_fb(input_vars_xml, output_vars_xml)
                    # virtualize (opc-ua) the method
                    method2call.virtualize(folder_idx, methods_path, method2call.method_name)

        # creates the variables folder
        folder_idx, vars_path, vars_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                self.base_path, self.base_path_list, 'Variables')
        # Iterates over the input_vars
        for entry in input_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if 'Variable' in var_specs:
                    # create the variable
                    var_idx, var_object = self.create_fb_variable(var_specs, folder_idx, vars_path)
                    # adds the variable to the dictionary
                    self.ua_variables[var_specs.attrib['Name']] = var_object

    def __create_header_objects(self):
        # creates the device object
        self.create_base_object(self.fb_name)
        # creates the fb_type property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                               property_name='SourceType', property_value=self.fb_type)
        # creates the state property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                               property_name='SourceState', property_value=self.state)
        # create the id property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', self.subs_id)

    def __parse_header(self, header_xml):
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

                            # creates the fb
                            elif element.attrib['id'] == 'SourceType':
                                self.fb_type = element.text

                            # creates the state
                            elif element.attrib['id'] == 'SourceState':
                                self.state = element.text

        self.__create_header_objects()

    def __parse_methods(self, methods_xml):
        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                      self.base_path, self.base_path_list, 'Methods')
        for method in methods_xml:
            method_name = method.attrib['name']

            # gets the created fb
            fb = self.ua_peer.config.get_fb(self.fb_name)

            method2call = utils.Method2Call(method_name, fb, self.ua_peer)
            # parses the method from the xml
            method2call.from_xml(method)
            # virtualize (opc-ua) the method
            method2call.virtualize(folder_idx, methods_path, method2call.method_name)

    def __parse_variables(self, vars_xml):
        # creates the variables folder
        folder_idx, vars_path, vars_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                self.base_path, self.base_path_list, 'Variables')
        # creates the opc-ua variables and links them
        for var in vars_xml:
            if var.attrib['name'] != 'Description':
                # create the variable
                var_idx, var_object = self.create_variable(var, folder_idx, vars_path)
                # adds the variable to the dictionary
                self.ua_variables[var.attrib['name']] = var_object

    def __create_context_links(self, links_xml):
        # creates the subscriptions folder
        folder_idx, subs_path, subs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                self.base_path, self.base_path_list, 'Subscriptions')
        for subs in links_xml:
            # context connections between sensors/actuators and components/equipments
            pass
