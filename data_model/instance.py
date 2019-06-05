from data_model import utils
from opcua import ua


class InstanceService(utils.DiacInterface):

    def __init__(self, ua_peer, service_base):
        utils.DiacInterface.__init__(self, ua_peer, 'ServiceInstanceSet')
        self.fb_type = service_base.fb_type
        # service associated to this instance
        self.subs_did = service_base.subs_id
        # service xml variables
        self.variables_xml = service_base.variables_xml
        # create the opc-ua method to call
        self.ua_method = None

    def from_xml(self, root_xml):
        # gets the instance_id
        self.subs_id = root_xml.attrib['id']
        self.fb_name = root_xml.attrib['id']

        # creates the header opc-ua (description, ...) of this instance
        self.__create_header(root_xml)

        # creates the fb for the instance
        self.ua_peer.config.create_virtualized_fb(self.subs_id, self.fb_type, self.update_variables)

        # create the ua method to call
        self.ua_method = utils.Method2Call('Run', self.ua_peer.config.get_fb(self.fb_name), self.ua_peer)
        # create the linked variables
        self.__create_variables(None)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'methods':
                # creates the default methods 'AddLink', 'RemoveLink' and 'DeleteInstance'
                self.__create_methods(item)

            elif tag == 'subscriptions':
                self.__create_links(item)

    def __create_header(self, header_xml):
        # creates the instance object
        browse_name = '{0}:{1}'.format(self.fb_type, self.subs_id)
        self.create_base_object(browse_name)

        # creates the id and dId property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', self.subs_id)
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'dID', self.subs_did)

    def __create_methods(self, methods_xml):
        # create the folder for the methods
        folder_idx, folder_path, folder_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                    self.base_path, self.base_path_list, 'Methods')
        for method in methods_xml:
            if method.attrib['name'] == 'AddLink':
                # creates the opc-ua method 'AddLink'
                method_idx = '{0}:{1}'.format(folder_idx, 'AddLink')
                browse_name = '2:{0}'.format('AddLink')
                self.ua_peer.create_method(folder_path,
                                           method_idx,
                                           browse_name,
                                           self.add_ua_link,
                                           input_args=[ua.VariantType.String],
                                           output_args=[])

            elif method.attrib['name'] == 'RemoveLink':
                # creates the opc-ua method 'RemoveLink'
                method_idx = '{0}:{1}'.format(folder_idx, 'RemoveLink')
                browse_name = '2:{0}'.format('RemoveLink')
                self.ua_peer.create_method(folder_path,
                                           method_idx,
                                           browse_name,
                                           self.remove_ua_link,
                                           input_args=[ua.VariantType.String],
                                           output_args=[])

            elif method.attrib['name'] == 'DeleteInstance':
                # creates the opc-ua method 'DeleteInstance'
                method_idx = '{0}:{1}'.format(folder_idx, 'DeleteInstance')
                browse_name = '2:{0}'.format('DeleteInstance')
                self.ua_peer.create_method(folder_path,
                                           method_idx,
                                           browse_name,
                                           self.delete_ua,
                                           input_args=[],
                                           output_args=[])

            elif method.attrib['name'] == 'CallInstance':
                self.ua_method.virtualize(folder_idx, folder_path, 'CallInstance')

    def __create_links(self, links_xml):
        # creates the subscriptions folder
        folder_idx, folder_path, folder_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                    self.base_path, self.base_path_list,
                                                                    'Subscriptions')
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
                    # gets the destination fb
                    content = self.ua_peer.search_id(sub_splitted[0])
                    # creates the connection between the fb
                    source = '{0}.{1}'.format(self.subs_id, subscription.attrib['VariableName'])
                    destination = '{0}.{1}'.format(content.fb_name, sub_splitted[2])
                    self.ua_peer.config.create_connection(source=source, destination=destination)
                    # connect the output event to input event

                # its an output variable
                elif subscription.attrib['BrowseDirection'] == 'inverse':
                    pass

    def __create_variables(self, vars_xml):
        # creates the subscriptions folder
        folder_idx, folder_path, folder_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                    self.base_path, self.base_path_list, 'Variables')
        for var_xml in self.variables_xml:
            # creates the variable
            var_idx, var_object = self.create_variable(var_xml, folder_idx, folder_path)
            var_path = self.ua_peer.generate_path(folder_list + [(2, var_xml.attrib['name'])])
            # creates the type property
            for ele in var_xml[0]:
                if ele.attrib['id'] == 'Type':
                    utils.default_property(self.ua_peer, var_idx, var_path, 'Type', ele.text)
            # parse the variable in the ua method
            self.ua_method.parse_variable(var_xml)
            # link the variables object to update
            self.ua_variables[var_xml.attrib['name']] = var_object

    def add_ua_link(self, parent, *args):
        print('adding link')
        return []

    def remove_ua_link(self, parent, *args):
        print('removing link')
        return []

    def delete_ua(self, parent, *args):
        print('deleting instance')
        return []
