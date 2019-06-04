from data_model import utils
from opcua import ua


class Service(utils.UaBaseStructure):

    def __init__(self, ua_peer):
        utils.UaBaseStructure.__init__(self, ua_peer, 'ServiceDescriptionSet')
        # key: constant_name, value: value to set (converted)
        self.constants = dict()
        self.subscriptions = dict()
        # all instances from this service
        # key: instance_id, value: instance_obj
        self.__instances = dict()

    def service_from_xml(self, root_xml):
        """
        service.name         -> fb_type
        recipe_adjustment
            parameter        -> input_vars   (use config.write_connection)
        interfaces
            inputs           -> input_vars   (use set_attr)
            outputs          -> output_vars  (use read_attr)
        method
            add_instance     -> input_events (use push_event)
                             -> connect to add_instance logic

        events to run method
            Run    (input_event)
            Run_O  (output_event)

        :param root_xml:
        """
        self.fb_type = root_xml.attrib['name']
        self.subs_id = root_xml.attrib['dId']

        # creates the service
        self.create_base_object(browse_name=self.fb_type)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'recipeadjustments':
                # sets the constant variables values
                self.__create_recipe_adjustments(item)

            elif tag == 'methods':
                # sets the method 'CreateInstance'
                self.__create_methods(item)

            elif tag == 'interfaces':
                # parses the info from each interface
                self.__create_interfaces(item)

    def __create_methods(self, methods_xml):
        # creates the methods folder
        folder_idx, methods_path = utils.default_folder(self.ua_peer,
                                                        self.base_idx, self.base_path, self.base_path_list,
                                                        'Methods')
        # creates each different method
        for method_xml in methods_xml:
            # case method create instance
            if method_xml.attrib['name'] == 'CreateInstance':
                # creates the opc-ua method
                method_idx = '{0}:{1}'.format(folder_idx, 'CreateInstance')
                self.ua_peer.create_method(methods_path,
                                           method_idx,
                                           '2:CreateInstance',
                                           self.instance_from_ua,
                                           input_args=[],
                                           output_args=[])

    def __create_recipe_adjustments(self, adj_xml):
        # creates the Recipe Adjustments folder
        folder_idx, adjustments_path = utils.default_folder(self.ua_peer,
                                                            self.base_idx, self.base_path, self.base_path_list,
                                                            'RecipeAdjustments')

    def __create_interfaces(self, if_xml):
        # creates the interfaces folder
        folder_idx, interfaces_path = utils.default_folder(self.ua_peer,
                                                           self.base_idx, self.base_path, self.base_path_list,
                                                           'Interfaces')

    def instance_from_xml(self, root_xml):
        # creates and parses the instance
        instance = InstanceService(self.ua_peer, self)
        instance.from_xml(root_xml)
        # adds the method to the dict
        self.__instances[instance.subs_id] = instance

    def get_instance(self, instance_id):
        if instance_id in self.__instances:
            return self.__instances[instance_id]
        else:
            return None

    def instance_from_ua(self, parent, *args):
        print('create instance')
        return []


class InstanceService(utils.DiacInterface):

    def __init__(self, ua_peer, service_base):
        utils.DiacInterface.__init__(self, ua_peer, 'ServiceInstanceSet')
        self.fb_type = service_base.fb_type
        self.subs_did = service_base.subs_id

    def from_xml(self, root_xml):
        # gets the instance_id
        self.subs_id = root_xml.attrib['id']
        self.fb_name = root_xml.attrib['id']

        # creates the header opc-ua (description, ...) of this instance
        self.__create_header(root_xml)

        # creates the fb for the instance
        self.ua_peer.config.create_virtualized_fb(self.subs_id, self.fb_type, self.update_variables)

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
        folder_idx, folder_path = utils.default_folder(self.ua_peer,
                                                       self.base_idx, self.base_path, self.base_path_list,
                                                       'Methods')
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

    def __create_links(self, links_xml):
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

    def __create_variables(self, variables_xml):
        pass

    def add_ua_link(self, parent, *args):
        print('adding link')
        return []

    def remove_ua_link(self, parent, *args):
        print('removing link')
        return []

    def delete_ua(self, parent, *args):
        print('deleting instance')
        return []

