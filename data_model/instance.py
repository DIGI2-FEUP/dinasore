from data_model import utils
import xml.etree.ElementTree as ETree
from opcua import ua


class InstanceService(utils.UaBaseStructure, utils.UaInterface):

    def __init__(self, ua_peer, service_id, var_list, subs_id, fb_name, fb_type):
        # creates the instance object
        utils.UaBaseStructure.__init__(self, ua_peer, 'ServiceInstanceSet',
                                       subs_id=subs_id,
                                       fb_name=fb_name,
                                       fb_type=fb_type,
                                       browse_name=subs_id)
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

            # parses the subscriptions
            if tag == 'subscriptions':
                self.parse_subscriptions(item)

    def from_fb(self, fb, fb_xml):
        # pass the method to update the variables
        fb.ua_variables_update = self.update_variables

        # creates the instance
        self.__create_instance()

    def save_xml(self, xml_set):
        # sets the attributes of that instance
        xml_set.attrib['id'] = self.subs_id
        xml_set.attrib['dId'] = self.subs_did

        # creates the subscriptions xml
        subscriptions_xml = ETree.SubElement(xml_set, 'subscriptions')

        # iterates over the subscriptions
        for subs_name, subs_value in self.subscriptions_dict.items():
            # creates the subscription
            subs_xml = ETree.SubElement(subscriptions_xml, 'id')
            subs_xml.attrib['BrowseDirection'] = 'forward'
            subs_xml.attrib['type'] = 'Data'
            subs_xml.attrib['VariableName'] = subs_name

            # gets the node_id
            node_id = None
            for item in subs_value.nodeid.to_string().split(';'):
                if item[:2] == 's=':
                    node_id = item[2:]
            subs_xml.text = node_id

        # writes the constant values
        for var in self.variables_list:
            if var['Type'] == 'Constant':
                # creates the subscription
                subs_xml = ETree.SubElement(subscriptions_xml, 'id')
                subs_xml.attrib['BrowseDirection'] = 'both'
                subs_xml.attrib['type'] = 'Data'
                subs_xml.attrib['VariableName'] = var['Name']
                var_ref = self.ua_peer.get_node('ns=2;s={0}:Variables:{1}'.format(self.subs_id, var['Name']))
                subs_xml.text = str(var_ref.get_value())

    def __create_instance(self):
        # create the ua method to call
        fb = self.ua_peer.config.get_fb(self.fb_name)

        # creates the connection to initialize the fb
        self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))

        # virtualize the method that allows the remote running
        self.ua_method = utils.Method2Call('RUN', fb, self.ua_peer)

        # create the linked variables
        for var_dict in self.variables_list:
            # creates the variable
            var_idx, var_object, var_path = self.virtualize_dict_variable(var_dict)
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

    def add_ua_link(self, parent, *args):
        print('adding link')
        return []

    def remove_ua_link(self, parent, *args):
        print('removing link')
        return []

    def delete_ua(self, parent, *args):
        print('deleting instance')
        return []
