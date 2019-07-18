from data_model import utils
import xml.etree.ElementTree as ETree


class Device(utils.UaBaseStructure, utils.UaInterface):

    def __init__(self, ua_peer, subs_id, fb_name, fb_type, state, root_folder):
        utils.UaBaseStructure.__init__(self, ua_peer, root_folder,
                                       subs_id=subs_id,
                                       fb_name=fb_name,
                                       fb_type=fb_type,
                                       browse_name=fb_name)
        self.state = state
        self.fb_general_type = 'DEVICE'
        self.ua_methods = dict()

        # creates the fb_type property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                               property_name='SourceType', property_value=self.fb_type)
        # creates the state property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                               property_name='SourceState', property_value=self.state)
        # create the id property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', self.subs_id)

    def from_xml(self, root_xml):
        # creates the fb inside the configuration
        self.ua_peer.config.create_virtualized_fb(self.fb_name, self.fb_type, self.update_variables)

        if self.fb_general_type == 'DEVICE':
            self.fb_general_type = root_xml.attrib['type']

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'variables':
                # link opc-ua variables in fb input variable
                # creates the opc-ua variables and links them
                for var in item:
                    if var.attrib['name'] != 'Description':
                        # create the variable
                        var_idx, var_object, var_path = self.virtualize_xml_variable(var)
                        # adds the variable to the dictionary
                        self.ua_variables[var.attrib['name']] = var_object

            elif tag == 'methods':
                # link opc-ua methods in fb methods
                for method in item:
                    method_name = method.attrib['name']

                    # gets the created fb
                    fb = self.ua_peer.config.get_fb(self.fb_name)

                    method2call = utils.Method2Call(method_name, fb, self.ua_peer)
                    # parses the method from the xml
                    method2call.from_xml(method)
                    # virtualize (opc-ua) the method
                    method2call.virtualize(self.methods_idx, self.methods_path, method2call.method_name)
                    # save the method in the dictionary
                    self.ua_methods[method_name] = method2call

            elif tag == 'subscriptions':
                # parse the subscriptions
                self.parse_subscriptions(item)

        # link variable to the start fb (sensor to init fb)
        if self.fb_general_type == 'SENSOR' or self.fb_general_type == 'STARTPOINT':
            self.create_extras()

    def from_fb(self, fb, fb_xml):
        # parses the fb description
        fb_id, ua_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
            utils.parse_fb_description(fb_xml)

        if self.fb_general_type == 'DEVICE':
            # gets the type of device
            self.fb_general_type = ua_type.split('.')[1]

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
                    method2call.virtualize(self.methods_idx, self.methods_path, method2call.method_name)
                    # save the method in the dictionary
                    self.ua_methods[method_name] = method2call

        # Iterates over the input_vars
        for entry in input_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if 'Variable' in var_specs:
                    # create the variable
                    var_idx, var_object, var_path = self.virtualize_fb_variable(entry)
                    # adds the variable to the dictionary
                    self.ua_variables[entry.attrib['Name']] = var_object
                elif 'Constant' in var_specs:
                    # create the variable
                    var_idx, var_object, var_path = self.virtualize_fb_variable(entry)
                    # adds the variable to the dictionary
                    self.ua_variables[entry.attrib['Name']] = var_object
                    # adds the constant to the list
                    self.variables_list.append({'Name': entry.attrib['Name'], 'Type': 'Constant'})

        # Iterates over the output_vars
        for entry in output_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if 'Variable' in var_specs:
                    # create the variable
                    var_idx, var_object, var_path = self.virtualize_fb_variable(entry)
                    # adds the variable to the dictionary
                    self.ua_variables[entry.attrib['Name']] = var_object

        # pass the method to update the variables
        fb.ua_variables_update = self.update_variables

        # link variable to the start fb (sensor to init fb)
        if self.fb_general_type == 'SENSOR' or self.fb_general_type == 'STARTPOINT':
            self.create_extras()

    def save_xml(self, device_xml):
        # receives a device xml element
        device_xml.attrib['id'] = self.subs_id
        device_xml.attrib['type'] = self.fb_general_type

        # creates the variables xml
        variables_xml = ETree.SubElement(device_xml, 'variables')

        # creates the description variable
        description_xml = ETree.SubElement(variables_xml, 'variable')
        description_xml.attrib = {'name': 'Description', 'DataType': 'String', 'ValueRank': '-1'}
        # creates the elements tag
        elements_xml = ETree.SubElement(description_xml, 'elements')
        # adds the name to the description
        name_xml = ETree.SubElement(elements_xml, 'element')
        name_xml.attrib = {'id': 'Name', 'DataType': 'String', 'ValueRank': '-1'}
        name_xml.text = self.fb_name
        # adds the state to the description
        state_xml = ETree.SubElement(elements_xml, 'element')
        state_xml.attrib = {'id': 'SourceState', 'DataType': 'String', 'ValueRank': '-1'}
        state_xml.text = self.state
        # adds the type to the description
        type_xml = ETree.SubElement(elements_xml, 'element')
        type_xml.attrib = {'id': 'SourceType', 'DataType': 'String', 'ValueRank': '-1'}
        type_xml.text = self.fb_type

        # gets the variables object
        vars_object = self.ua_peer.get_object(self.vars_path)
        children = vars_object.get_children()
        for child in children:
            # creates each variables
            var_xml = ETree.SubElement(variables_xml, 'variable')
            var_xml.attrib = {'name': child.get_display_name().to_string(),
                              'DataType': utils.XML_TYPES[child.get_data_type_as_variant_type()],
                              'ValueRank': str(child.get_value_rank())}

        # creates the methods xml
        methods_xml = ETree.SubElement(device_xml, 'methods')
        # iterates over each method
        for method_name, ua_method in self.ua_methods.items():
            # creates the xml method
            method_xml = ETree.SubElement(methods_xml, 'method')
            # saves the method inside the xml
            ua_method.save_xml(method_xml)

        # saves the subscriptions
        subscriptions_xml = ETree.SubElement(device_xml, 'subscriptions')
        # saves the constant values
        for variable_item in self.variables_list:
            # checks if is a constant
            if variable_item['Type'] == 'Constant':
                # creates the constant xml
                subs_xml = ETree.SubElement(subscriptions_xml, 'id')
                subs_xml.attrib['BrowseDirection'] = 'both'
                subs_xml.attrib['type'] = 'Data'
                subs_xml.attrib['VariableName'] = variable_item['Name']
                var_ref = self.ua_peer.get_node('ns=2;s={0}:Variables:{1}'.format(self.subs_id, variable_item['Name']))
                subs_xml.text = str(var_ref.get_value())
