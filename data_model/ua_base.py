from data_model import ua_method
from data_model import utils
from opcua import ua
import xml.etree.ElementTree as ETree
import uuid
import logging


class UaBaseStructure:

    def __init__(self, ua_peer, folder_name, fb_name, fb_type, browse_name):
        self.fb_name = fb_name
        self.fb_type = fb_type
        self.ua_peer = ua_peer
        self.folder_name = folder_name

        # creates the path to set the folder
        folder_path_list = self.ua_peer.ROOT_LIST + [(2, self.folder_name)]
        folder_path = self.ua_peer.generate_path(folder_path_list)

        self.base_idx = 'ns=2;s={0}'.format(self.fb_name)
        # creates the device object
        base_path_list, self.base_path = utils.default_object(self.ua_peer, self.base_idx, folder_path,
                                                              folder_path_list,
                                                              browse_name)

        # creates the methods folder
        self.methods_idx, self.methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                                 self.base_path, base_path_list,
                                                                                 'Methods')
        self.methods_dict = dict()

        # creates the variables folder
        self.vars_idx, self.vars_path, vars_list = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                        base_path_list, 'Variables')
        self.ua_variables = dict()
        self.variables_dict = dict()

        # creates the subscriptions folder
        self.subs_idx, subs_path, subs_list = utils.default_folder(self.ua_peer, self.base_idx, self.base_path,
                                                                   base_path_list, 'Subscriptions')
        self.subscriptions_folder = self.ua_peer.get_object(subs_path)
        # creates the dictionary where are stored the connections
        self.subscriptions_dict = dict()

    def virtualize_variable(self, var_xml):
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
        for variable_name, variable in self.variables_dict.items():
            # creates each variables
            var_xml = ETree.SubElement(variables_xml, 'variable')
            var_xml.attrib['name'] = variable['name']
            var_xml.attrib['ValueRank'] = str(variable['ValueRank'])
            var_xml.attrib['DataType'] = utils.XML_4DIAC[str(variable['DataType'])]
            var_xml.attrib['ArrayDimensions'] = str(variable['ArrayDimensions'])

    def __dm_method(self, method_xml):
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
                    self.subscriptions_dict[subscription.attrib['VariableName']] = {'BrowseDirection': 'forward',
                                                                                    'type': 'Data',
                                                                                    'value': subscription.text}
                # its a constant
                elif subscription.attrib['BrowseDirection'] == 'both':
                    # gets the value to write
                    source = subscription.text
                    destination = '{0}.{1}'.format(self.fb_name, subscription.attrib['VariableName'])
                    # write the value in the fb
                    self.ua_peer.config.write_connection(source_value=source, destination=destination)
                    # saves the subscription in the dictionary
                    self.subscriptions_dict[subscription.attrib['VariableName']] = {'BrowseDirection': 'both',
                                                                                    'type': 'Data',
                                                                                    'value': subscription.text}

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
                    self.subscriptions_dict[subscription.attrib['VariableName']] = {'BrowseDirection': 'forward',
                                                                                    'type': 'Event',
                                                                                    'value': subscription.text}

    def __save_subscriptions(self, subscriptions_xml):
        for subscription_name, subscription in self.subscriptions_dict.items():
            # creates the subscription
            subs_xml = ETree.SubElement(subscriptions_xml, 'id')
            subs_xml.attrib['BrowseDirection'] = subscription['BrowseDirection']
            subs_xml.attrib['type'] = subscription['type']
            subs_xml.attrib['VariableName'] = subscription_name
            subs_xml.text = subscription['value']

    def fb_connection_subscription(self, source, destination):
        # splits both source and destination (fb, fb_variable)
        source_attr = source.split(sep='.')
        destination_attr = destination.split(sep='.')

        if destination_attr[1] in self.ua_peer.config.get_fb(destination_attr[0]).input_events:
            # builds the node_id for the source
            node_id = '{0}:Events:{1}'.format(source_attr[0], source_attr[1])

            # saves the subscription in the dictionary
            self.subscriptions_dict[destination_attr[1]] = {'BrowseDirection': 'forward',
                                                            'type': 'Event',
                                                            'value': node_id}

        elif destination_attr[1] in self.ua_peer.config.get_fb(destination_attr[0]).input_vars:
            # builds the node_id for the source
            node_id = '{0}:Variables:{1}'.format(source_attr[0], source_attr[1])

            # adds that subscription to the folder
            var_ref = self.ua_peer.get_node('ns=2;s={0}'.format(node_id))
            self.subscriptions_folder.add_reference(var_ref, ua.ObjectIds.Organizes)

            # saves the subscription in the dictionary
            self.subscriptions_dict[destination_attr[1]] = {'BrowseDirection': 'forward',
                                                            'type': 'Data',
                                                            'value': node_id}

    def fb_write_subscription(self, source_value, destination):
        destination_attr = destination.split(sep='.')
        # saves the subscription in the dictionary
        self.subscriptions_dict[destination_attr[1]] = {'BrowseDirection': 'both',
                                                        'type': 'Data',
                                                        'value': source_value}

    def create_extra_fb(self):
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

    def parse_all_xml(self, root_xml):
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

            elif tag == 'subscriptions':
                # parse the subscriptions
                self.__parse_subscriptions(item)

    def parse_all_fb(self, fb, fb_xml):
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


class UaBaseLayer2(UaBaseStructure):

    def __init__(self, ua_peer, fb_name, fb_type, root_folder, source_type):
        UaBaseStructure.__init__(self, ua_peer, root_folder,
                                 fb_name=fb_name,
                                 fb_type=fb_type,
                                 browse_name=fb_name)
        self.source_type = source_type
        # creates the id and dId property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', self.fb_name)
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'dID', self.fb_type)
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'SourceType', self.source_type)

    def parse_loop_type_xml(self, root_xml):
        self.parse_all_xml(root_xml)
        self.create_extra_fb()

    def parse_loop_type_fb(self, fb, fb_xml):
        self.parse_all_fb(fb, fb_xml)
        self.create_extra_fb()

    def parse_service_type_xml(self, item_xml):
        self.parse_all_xml(item_xml)
        # create the ua method to call
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # creates the connection to initialize the fb
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))
        # virtualize the method that allows the remote running
        ua_method.Method2Call('RUN', fb, self.ua_peer)

    def parse_service_type_fb(self, fb, fb_xml):
        self.parse_all_fb(fb, fb_xml)
        # create the ua method to call
        fb = self.ua_peer.config.get_fb(self.fb_name)
        # creates the connection to initialize the fb
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))
        # virtualize the method that allows the remote running
        ua_method.Method2Call('RUN', fb, self.ua_peer)
