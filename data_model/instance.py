from data_model import utils
from data_model import device
from opcua import ua


class InstanceService(utils.UaBaseStructure):

    def __init__(self, ua_peer, service_id, var_list, subs_id, fb_name, fb_type):
        # creates the instance object
        browse_name = '{0}:{1}'.format(fb_type, subs_id)
        utils.UaBaseStructure.__init__(self, ua_peer, 'ServiceInstanceSet',
                                       subs_id=subs_id,
                                       fb_name=fb_name,
                                       fb_type=fb_type,
                                       browse_name=browse_name)
        # service associated to this instance
        self.subs_did = service_id
        # service xml variables
        self.variables_list = var_list
        # create the opc-ua method to call
        self.ua_method = None

        # creates the id and dId property
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', self.subs_id)
        utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'dID', self.subs_did)

    def from_xml(self, root_xml):
        # creates the fb for the instance
        self.ua_peer.config.create_virtualized_fb(self.subs_id, self.fb_type, self.update_variables)

        # creates the instance
        self.__create_instance()

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")
            if tag == 'subscriptions':
                self.__parse_subscriptions(item)

    def from_fb(self, fb):
        # pass the method to update the variables
        fb.ua_variables_update = self.update_variables

        # creates the instance
        self.__create_instance()

    def __create_instance(self):
        # create the ua method to call
        fb = self.ua_peer.config.get_fb(self.fb_name)
        self.ua_method = utils.Method2Call('Run', fb, self.ua_peer)

        # create the linked variables
        for var_dict in self.variables_list:
            # creates the variable
            var_idx, var_object = self.create_variable_by_dict(var_dict)
            var_path = self.ua_peer.generate_path(self.vars_list + [(2, var_dict['Name'])])
            # creates the type property
            utils.default_property(self.ua_peer, var_idx, var_path, 'Type', var_dict['Type'])
            # parse the variable in the ua method
            self.ua_method.parse_variable(var_dict)
            # link the variables object to update
            self.ua_variables[var_dict['Name']] = var_object

        # creates the default methods 'AddLink', 'RemoveLink' and 'DeleteInstance'
        # creates the opc-ua method 'AddLink'
        method_idx = '{0}:{1}'.format(self.methods_idx, 'AddLink')
        browse_name = '2:{0}'.format('AddLink')
        self.ua_peer.create_method(self.methods_path, method_idx, browse_name, self.add_ua_link,
                                   input_args=[ua.VariantType.String], output_args=[])
        # creates the opc-ua method 'RemoveLink'
        method_idx = '{0}:{1}'.format(self.methods_idx, 'RemoveLink')
        browse_name = '2:{0}'.format('RemoveLink')
        self.ua_peer.create_method(self.methods_path, method_idx, browse_name, self.remove_ua_link,
                                   input_args=[ua.VariantType.String], output_args=[])
        # creates the opc-ua method 'DeleteInstance'
        method_idx = '{0}:{1}'.format(self.methods_idx, 'DeleteInstance')
        browse_name = '2:{0}'.format('DeleteInstance')
        self.ua_peer.create_method(self.methods_path, method_idx, browse_name, self.delete_ua,
                                   input_args=[], output_args=[])

        self.ua_method.virtualize(self.methods_idx, self.methods_path, 'CallInstance')

    def __parse_subscriptions(self, links_xml):
        # creates the subscriptions folder
        utils.default_folder(self.ua_peer, self.base_idx, self.base_path, self.base_path_list, 'Subscriptions')
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
                    source = '{0}.{1}'.format(content.fb_name, sub_splitted[2])
                    destination = '{0}.{1}'.format(self.subs_id, subscription.attrib['VariableName'])
                    self.ua_peer.config.create_connection(source=source, destination=destination)
                    # connect the output event to input event
                    if isinstance(content, device.Device):
                        source_event = '{0}.{1}'.format(content.fb_name, 'Read_O')
                    else:
                        source_event = '{0}.{1}'.format(content.fb_name, 'Run_O')

                    # creates the connection between the fb
                    destination_event = '{0}.{1}'.format(self.subs_id, 'Run')
                    self.ua_peer.config.create_connection(source=source_event, destination=destination_event)

                # its an output variable
                elif subscription.attrib['BrowseDirection'] == 'inverse':
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
