import xml.etree.ElementTree as ETree
from data_model import utils
from data_model import ua_object


class ServiceSet(utils.UaInterface):

    def __init__(self, ua_peer):
        # service_id: service
        self.service_dict = dict()
        # receives the peer methods to add the opc-ua services
        self.__ua_peer = ua_peer

        # creates the service description opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'ServiceDescriptionSet')

    def from_xml(self, xml_set):
        for service_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = service_xml.tag[1:].partition("}")

            if tag == 'servicedescription':
                fb_type = service_xml.attrib['id']
                # creates the service
                s = Service(self.__ua_peer, fb_type)
                s.from_xml(service_xml)

                # use the service_id as key
                self.service_dict[s.fb_type] = s

    def from_fb(self, fb_type, fb_xml):
        input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
                utils.parse_fb_description(fb_xml)
        # checks if the service already exist in the service set
        if fb_type not in self.service_dict:
            # otherwise it creates the service
            s = Service(self.__ua_peer, fb_type)
            s.from_fb(input_vars_xml, output_vars_xml)
            # use the service_id as key
            self.service_dict[s.fb_type] = s

    def save_xml(self, xml_set):
        # iterates over the services dictionary
        for service_name, service_item in self.service_dict.items():
            # creates the service xml
            service_xml = ETree.SubElement(xml_set, 'servicedescription')
            # saves the content of that service
            service_item.save_xml(service_xml)


class Service(ua_object.UaObject, utils.UaInterface):

    def __init__(self, ua_peer, fb_type):
        ua_object.UaObject.__init__(self, ua_peer,
                                    fb_name='Service:' + fb_type,
                                    fb_type=fb_type,
                                    source_type='SERVICE',
                                    browse_name=fb_type,
                                    root_folder='ServiceDescriptionSet')

    def from_xml(self, root_xml):
        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # parses the input/output variables
            if tag == 'variables':
                # link opc-ua variables in fb input variable
                # creates the opc-ua variables and links them
                for var in item:
                    # parses the variable
                    self.virtualize_variable(var)

    def from_fb(self, input_vars_xml, output_vars_xml):
        # create the input variables interface
        for var_xml in input_vars_xml:
            if 'OpcUa' in var_xml.attrib:
                var_specs = var_xml.attrib['OpcUa'].split('.')
                if ('Variable' in var_specs) or ('Constant' in var_specs):
                    self.virtualize_variable(var_xml)

        # create the input variables interface
        for var_xml in output_vars_xml:
            if 'OpcUa' in var_xml.attrib:
                var_specs = var_xml.attrib['OpcUa'].split('.')
                if ('Variable' in var_specs) or ('Constant' in var_specs):
                    self.virtualize_variable(var_xml)

    def save_xml(self, service_xml):
        # sets the service xml attributes
        service_xml.attrib['id'] = self.fb_type
        service_xml.attrib['type'] = 'service'

        vars_xml = ETree.SubElement(service_xml, 'variables')
        # iterates over each variable
        self.save_variables(vars_xml)
