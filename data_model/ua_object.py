from data_model import ua_method
from data_model import utils
from opcua import ua
import xml.etree.ElementTree as ETree
import uuid
import logging


class UaObject:

    def __init__(self, ua_peer, fb_name, fb_type, source_type, browse_name, root_folder):
        """

        :param ua_peer:
        :param root_folder:
        :param fb_name:
        :param fb_type:
        :param browse_name:
        """
        self.fb_name = fb_name
        self.fb_type = fb_type
        self.ua_peer = ua_peer
        self.source_type = source_type

        # creates the path to set the folder
        folder_path_list = self.ua_peer.ROOT_LIST + [(2, root_folder)]
        folder_path = self.ua_peer.generate_path(folder_path_list)

        self.base_idx = 'ns=2;s={0}'.format(self.fb_name)
        # creates the device object
        self.base_path_list, self.base_path = utils.default_object(self.ua_peer, self.base_idx, folder_path,
                                                                   folder_path_list, browse_name)

        # creates the id and dId property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', self.fb_name)
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'dID', self.fb_type)
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'SourceType', self.source_type)

        # creates the methods folder
        self.methods_idx, self.methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                                 self.base_path, self.base_path_list,
                                                                                 'Methods')
        self.methods_dict = dict()

        # creates the variables folder
        self.vars_idx, self.vars_path, vars_list = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                        self.base_path_list, 'Variables')
        """
        the ua_variables contains:
        - variable_name: key
        - opc-ua variable: value
        the variables_dict contains:
        - variable_name: key and value
        - value_rank
        - data_type
        - array_dimensions
        """
        self.ua_variables = dict()
        self.variables_dict = dict()

        # creates the subscriptions folder
        self.subs_idx, subs_path, subs_list = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                   self.base_path_list, 'Subscriptions')
        self.subscriptions_folder = self.ua_peer.get_object(subs_path)
        # creates the dictionary where are stored the connections
        self.subscriptions_dict = dict()

    def virtualize_variable(self, var_xml):
        """
        Receives a variable in the XML format and creates it's OPC-UA representation.
        :param var_xml: XML variable from the data_model.xml or the function block XML.
        """
        # if is from a fb xml
        if 'name' and 'DataType' in var_xml.attrib:
            var_name = var_xml.attrib['name']
            var_type = var_xml.attrib['DataType']
        # if is from a data model xml
        elif 'Name' and 'Type' in var_xml.attrib:
            var_name = var_xml.attrib['Name']
            var_type = var_xml.attrib['Type']
        else:
            logging.error('error virtualize the variable')
            return

        # creates the opc-ua variable
        var_idx = '{0}:{1}'.format(self.vars_idx, var_name)
        browse_name = '2:{0}'.format(var_name)
        # convert array dimensions
        array_dimensions = 0
        var_rank = 0
        if 'ArrayDimensions' in var_xml.attrib:
            array_dimensions = int(var_xml.attrib['ArrayDimensions'])
        if 'ValueRank' in var_xml.attrib:
            var_rank = int(var_xml.attrib['ValueRank'])

        var_object = self.ua_peer.create_typed_variable(self.vars_path, var_idx, browse_name,
                                                        utils.UA_TYPES[var_type],
                                                        var_rank,
                                                        dimensions=array_dimensions,
                                                        writable=False)

        # save the variable in the dictionary
        self.variables_dict[var_name] = {'name': var_name,
                                         'ValueRank': var_rank,
                                         'DataType': var_type,
                                         'ArrayDimensions': array_dimensions}

        # adds the variable to the dictionary
        self.ua_variables[var_name] = var_object

    def save_variables(self, variables_xml):
        """
        Saves in the data_model.xml the variables stored in the variables_dict.
        :param variables_xml: XML tag where are stored the the variables
        """
        for variable_name, variable in self.variables_dict.items():
            # creates each variables
            var_xml = ETree.SubElement(variables_xml, 'variable')
            var_xml.attrib['name'] = variable['name']
            var_xml.attrib['ValueRank'] = str(variable['ValueRank'])
            var_xml.attrib['DataType'] = utils.XML_4DIAC[str(variable['DataType'])]
            var_xml.attrib['ArrayDimensions'] = str(variable['ArrayDimensions'])

    def update_variables(self):
        # gets the function block
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # iterates over the variables dict
        for var_name, var_ua in self.ua_variables.items():
            # reads the variable value
            v_type, value, is_watch = fb.read_attr(var_name)

            try:
                # writes the value inside the opc-ua variable
                var_ua.set_value(value)

            except Exception as error:
                # reports the error
                logging.warning('error writing the value in the opc-ua server.')
                logging.warning(error)
                if v_type == 'STRING':
                    # writes the value as a string
                    var_ua.set_value(str(value))
                    # writes the solution
                    logging.warning('error solved writing the variable as string.')

    def __dm_method(self, method_xml):
        """
        Receives a method in the XML format and creates it's OPC-UA representation.
        The XML representation comes from the data model XML.
        :param method_xml: XML method from the data_model.xml.
        """
        method_name = method_xml.attrib['name']

        # gets the created fb
        fb = self.ua_peer.config.get_fb(self.fb_name)

        method2call = ua_method.Method2Call(method_name, fb, self.ua_peer)
        # parses the method from the xml
        method2call.from_xml(method_xml)
        # virtualize (opc-ua) the method
        method2call.virtualize(self.methods_idx, self.methods_path, method2call.method_name)
        # save the method in the dictionary
        self.methods_dict[method_name] = method2call

    def __fb_method(self, input_event, input_vars_xml, output_vars_xml):
        """
        Receives a method in the XML format and creates it's OPC-UA representation.
        The XML representation comes from the function block XML.
        :param input_event: event that represents the method name.
        :param input_vars_xml: method input variables XML
        :param output_vars_xml: method output variables XML
        """
        # gets the method name
        method_name = input_event.attrib['Name']
        # gets the created fb
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # creates the opc-ua method
        method2call = ua_method.Method2Call(method_name, fb, self.ua_peer)
        # parses the inputs_vars and the output_vars
        method2call.from_fb(input_vars_xml, output_vars_xml)
        # virtualize (opc-ua) the method
        method2call.virtualize(self.methods_idx, self.methods_path, method2call.method_name)
        # save the method in the dictionary
        self.methods_dict[method_name] = method2call

    def __save_methods(self, methods_xml):
        # iterates over each method
        for method_name, method_item in self.methods_dict.items():
            # creates the xml method
            method_xml = ETree.SubElement(methods_xml, 'method')
            # saves the method inside the xml
            method_item.save_xml(method_xml)

    def __parse_subscriptions(self, links_xml):
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
                    # creates the connection between the fb
                    source = '{0}.{1}'.format(sub_splitted[0], sub_splitted[2])
                    destination = '{0}.{1}'.format(self.fb_name, subscription.attrib['VariableName'])
                    self.ua_peer.config.create_connection(source=source, destination=destination)

                    # adds that subscription to the folder
                    var_ref = self.ua_peer.get_node('ns=2;s={0}'.format(subscription.text))
                    self.subscriptions_folder.add_reference(var_ref, ua.ObjectIds.Organizes)
                    # saves the subscription in the dictionary
                    self.__add_subscription_collision(key=subscription.attrib['VariableName'],
                                                      value={'BrowseDirection': 'forward',
                                                             'type': 'Data',
                                                             'value': subscription.text})
                # its a constant
                elif subscription.attrib['BrowseDirection'] == 'both':
                    # gets the value to write
                    source = subscription.text
                    destination = '{0}.{1}'.format(self.fb_name, subscription.attrib['VariableName'])
                    # write the value in the fb
                    self.ua_peer.config.write_connection(source_value=source, destination=destination)
                    # saves the subscription in the dictionary
                    self.__add_subscription_collision(key=subscription.attrib['VariableName'],
                                                      value={'BrowseDirection': 'both',
                                                             'type': 'Data',
                                                             'value': subscription.text})
            # checks if is data subscription
            elif subscription.attrib['type'] == 'Event':
                # its an input event
                if subscription.attrib['BrowseDirection'] == 'forward':
                    # parses the subscription
                    sub_splitted = subscription.text.split(':')
                    # creates the connection between the fb
                    source = '{0}.{1}'.format(sub_splitted[0], sub_splitted[2])
                    destination = '{0}.{1}'.format(self.fb_name, subscription.attrib['VariableName'])
                    self.ua_peer.config.create_connection(source=source, destination=destination)
                    # saves the subscription in the dictionary
                    self.__add_subscription_collision(key=subscription.attrib['VariableName'],
                                                      value={'BrowseDirection': 'forward',
                                                             'type': 'Event',
                                                             'value': subscription.text})

    def __save_subscriptions(self, subscriptions_xml):
        for subscription_name, subscription_list in self.subscriptions_dict.items():
            # iterates over each list of subscriptions
            for subscription in subscription_list:
                # creates the subscription
                subs_xml = ETree.SubElement(subscriptions_xml, 'id')
                subs_xml.attrib['BrowseDirection'] = subscription['BrowseDirection']
                subs_xml.attrib['type'] = subscription['type']
                subs_xml.attrib['VariableName'] = subscription_name
                subs_xml.text = subscription['value']

    def __add_subscription_collision(self, key, value):
        """
        Adds a subscription avoiding the collision with other subscriptions.
        :param key:
        :param value:
        :return:
        """
        if key in self.subscriptions_dict:
            # if exist adds an item to the list
            self.subscriptions_dict[key].append(value)
        else:
            # if not exists creates the list
            self.subscriptions_dict[key] = [value]

    def parse_subscriptions(self, root_xml):
        # parses only the subscriptions
        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'subscriptions':
                # parse the subscriptions
                self.__parse_subscriptions(item)

    def fb_connection_subscription(self, source, destination):
        # splits both source and destination (fb, fb_variable)
        source_attr = source.split(sep='.')
        destination_attr = destination.split(sep='.')

        if destination_attr[1] in self.ua_peer.config.get_fb(destination_attr[0]).input_events:
            # builds the node_id for the source
            node_id = '{0}:Events:{1}'.format(source_attr[0], source_attr[1])

            # saves the subscription in the dictionary
            self.__add_subscription_collision(key=destination_attr[1],
                                              value={'BrowseDirection': 'forward',
                                                     'type': 'Event',
                                                     'value': node_id})

        elif destination_attr[1] in self.ua_peer.config.get_fb(destination_attr[0]).input_vars:
            # builds the node_id for the source
            node_id = '{0}:Variables:{1}'.format(source_attr[0], source_attr[1])

            # adds that subscription to the folder
            var_ref = self.ua_peer.get_node('ns=2;s={0}'.format(node_id))
            self.subscriptions_folder.add_reference(var_ref, ua.ObjectIds.Organizes)

            # saves the subscription in the dictionary
            self.__add_subscription_collision(key=destination_attr[1],
                                              value={'BrowseDirection': 'forward',
                                                     'type': 'Data',
                                                     'value': node_id})

    def fb_write_subscription(self, source_value, destination):
        destination_attr = destination.split(sep='.')
        # saves the subscription in the dictionary
        self.__add_subscription_collision(key=destination_attr[1],
                                          value={'BrowseDirection': 'both',
                                                 'type': 'Data',
                                                 'value': source_value})

    def __parse_partial_xml(self, root_xml):
        """
        Parses the variables and the methods,
        because to make the connections (subscriptions)
        the variables and methods must be created.
        :param root_xml:
        """
        # creates the fb inside the configuration
        self.ua_peer.config.create_virtualized_fb(self.fb_name, self.fb_type, self.update_variables)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'variables':
                # link opc-ua variables in fb input variable
                # creates the opc-ua variables and links them
                for var in item:
                    # parses the variable
                    self.virtualize_variable(var)

            elif tag == 'methods':
                # link opc-ua methods in fb methods
                for method in item:
                    # parses the method
                    self.__dm_method(method)

    def __parse_all_fb(self, fb, fb_xml):
        # parses the fb description
        input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
            utils.parse_fb_description(fb_xml)

        # Iterates over the input events
        for event in input_events_xml:
            # check if is a opc-ua method
            if 'OpcUa' in event.attrib:
                if event.attrib['OpcUa'] == 'Method':
                    self.__fb_method(event, input_vars_xml, output_vars_xml)

        # Iterates over the input_vars
        for entry in input_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if ('Variable' in var_specs) or ('Constant' in var_specs):
                    self.virtualize_variable(entry)

        # Iterates over the output_vars
        for entry in output_vars_xml:
            if 'OpcUa' in entry.attrib:
                var_specs = entry.attrib['OpcUa'].split('.')
                if ('Variable' in var_specs) or ('Constant' in var_specs):
                    self.virtualize_variable(entry)

        # pass the method to update the variables
        fb.ua_variables_update = self.update_variables

    def save_all_xml(self, xml_set):
        # sets the attributes of that instance
        xml_set.attrib['id'] = self.fb_name
        xml_set.attrib['dId'] = self.fb_type
        xml_set.attrib['type'] = self.source_type

        # creates the variables xml
        variables_xml = ETree.SubElement(xml_set, 'variables')
        # saves the variables
        self.save_variables(variables_xml)

        # creates the methods xml
        methods_xml = ETree.SubElement(xml_set, 'methods')
        # iterates over each method
        self.__save_methods(methods_xml)

        # creates the subscriptions xml
        subscriptions_xml = ETree.SubElement(xml_set, 'subscriptions')
        # iterates over the subscriptions
        self.__save_subscriptions(subscriptions_xml)

    def refract_ua_name(self):
        change_name = True if ('UA_NAME' in self.variables_dict.keys()) and \
                              ('UA_NAME' in self.subscriptions_dict.keys()) and \
                              ('VALUE' in self.variables_dict.keys()) else False
        # if the option to change the ua variable is activated
        if change_name:
            # get the subscription value
            new_var_name = self.subscriptions_dict['UA_NAME'][0]['value']
            # gets the previous variables settings
            var_settings = self.variables_dict['VALUE']
            # remove all the current ua variables
            for var_name, var_ua in self.ua_variables.items():
                # deletes each variable
                var_ua.delete()
            # create the variable with the defined name
            var_idx = '{0}:{1}'.format(self.vars_idx, new_var_name)
            browse_name = '2:{0}'.format(new_var_name)
            # create the  variable
            var_object = self.ua_peer.create_typed_variable(self.vars_path, var_idx, browse_name,
                                                            utils.UA_TYPES[var_settings['DataType']],
                                                            var_settings['ValueRank'],
                                                            dimensions=var_settings['ArrayDimensions'],
                                                            writable=False)
            # update the variables dict
            self.ua_variables = {'VALUE': var_object}

    def refract_ua_equipment(self):
        # checks if is an equipment
        if self.source_type == 'EQUIPMENT':
            # creates the folders for the actuators and the sensors
            _, actuators_path, _ = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                        self.base_path_list, 'Actuators')
            actuators_obj = self.ua_peer.get_object(actuators_path)
            _, sensors_path, _ = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                      self.base_path_list, 'Sensors')
            sensors_obj = self.ua_peer.get_object(sensors_path)

            # create the subscriptions for the actuators
            if 'ACTUATORS' in self.subscriptions_dict:
                # iterates over the subscriptions list
                for subscription in self.subscriptions_dict['ACTUATORS']:
                    # splits the subscription items
                    subscription_items = subscription['value'].split(':')
                    # adds that subscription to the folder
                    obj_ref = self.ua_peer.get_node('ns=2;s={0}'.format(subscription_items[0]))
                    actuators_obj.add_reference(obj_ref, ua.ObjectIds.Organizes)

            # create the subscriptions for the sensors
            if 'SENSORS' in self.subscriptions_dict:
                # iterates over the subscriptions list
                for subscription in self.subscriptions_dict['SENSORS']:
                    # splits the subscription items
                    subscription_items = subscription['value'].split(':')
                    # adds that subscription to the folder
                    obj_ref = self.ua_peer.get_node('ns=2;s={0}'.format(subscription_items[0]))
                    sensors_obj.add_reference(obj_ref, ua.ObjectIds.Organizes)

    def __create_loop_extra_fb(self):
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

    def parse_loop_type_xml(self, root_xml):
        self.__parse_partial_xml(root_xml)
        self.__create_loop_extra_fb()

    def parse_loop_type_fb(self, fb, fb_xml):
        self.__parse_all_fb(fb, fb_xml)
        self.__create_loop_extra_fb()

    def parse_service_type_xml(self, item_xml):
        self.__parse_partial_xml(item_xml)
        # creates the connection to initialize the fb
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))

    def parse_service_type_fb(self, fb, fb_xml):
        self.__parse_all_fb(fb, fb_xml)
        # create the ua method to call
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # creates the connection to initialize the fb
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))
        # virtualize the method that allows the remote running
        ua_method.Method2Call('RUN', fb, self.ua_peer)
