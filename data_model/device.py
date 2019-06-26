from data_model import utils
import uuid


class Device(utils.UaBaseStructure):

    def __init__(self, ua_peer, subs_id, fb_name, fb_type, state):
        utils.UaBaseStructure.__init__(self, ua_peer, 'DeviceSet', subs_id, fb_name, fb_type)
        self.state = state

        self.__create_header_objects()

    def from_xml(self, root_xml):
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
                pass

        # link variable to the start fb (sensor to init fb)
        if root_xml.attrib['type'] == 'SENSOR':
            self.__create_sensor_extras()

    def from_fb(self, fb, fb_xml):
        # parses the fb description
        fb_id, ua_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
            utils.parse_fb_description(fb_xml)
        # gets the type of device
        device_type = ua_type.split('.')[1]

        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
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
        folder_idx, vars_path, vars_list = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                self.base_path_list, 'Variables')
        # Iterates over the input_vars
        for entry in input_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if 'Variable' in var_specs:
                    # create the variable
                    var_idx, var_object = self.create_fb_variable(entry, folder_idx, vars_path)
                    # adds the variable to the dictionary
                    self.ua_variables[entry.attrib['Name']] = var_object

        # Iterates over the output_vars
        for entry in output_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if 'Variable' in var_specs:
                    # create the variable
                    var_idx, var_object = self.create_fb_variable(entry, folder_idx, vars_path)
                    # adds the variable to the dictionary
                    self.ua_variables[entry.attrib['Name']] = var_object

        # pass the method to update the variables
        fb.ua_variables_update = self.update_variables

        # link variable to the start fb (sensor to init fb)
        if device_type == 'SENSOR':
            self.__create_sensor_extras()

    def __create_sensor_extras(self):
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'Init'))
        # creates the fb that runs the device in loop
        sleep_fb_name = str(uuid.uuid4())
        self.ua_peer.config.create_fb(sleep_fb_name, 'SLEEP')
        self.ua_peer.config.create_connection('{0}.{1}'.format(sleep_fb_name, 'SLEEP_O'),
                                              '{0}.{1}'.format(self.fb_name, 'Read'))
        self.ua_peer.config.create_connection('{0}.{1}'.format(self.fb_name, 'Read_O'),
                                              '{0}.{1}'.format(sleep_fb_name, 'SLEEP'))

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
