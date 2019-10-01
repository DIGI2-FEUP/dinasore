import xml.etree.ElementTree as ETree
from data_model import utils
from data_model import service
from data_model import ua_base


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
                s = service.Service(self.__ua_peer, fb_type)
                s.from_xml(service_xml)

                # use the service_id as key
                self.service_dict[s.fb_type] = s

    def from_fb(self, fb_type, fb_xml):
        input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
                utils.parse_fb_description(fb_xml)
        # checks if the service already exist in the service set
        if fb_type not in self.service_dict:
            # otherwise it creates the service
            s = service.Service(self.__ua_peer, fb_type)
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


class InstanceSet(utils.UaInterface):

    def __init__(self, ua_peer):
        self.instances_dict = dict()
        # receives the peer methods to add the opc-ua services
        self.__ua_peer = ua_peer

        # creates the service instance opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'ServiceInstanceSet')

    def from_xml(self, item_xml):
        for instance_xml in item_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = instance_xml.tag[1:].partition("}")

            if tag == 'serviceinstance':
                # gets the service id
                fb_type = instance_xml.attrib['dId']
                # connects the instance to the service
                fb_name = instance_xml.attrib['id']
                inst = ua_base.UaBaseLayer2(self.__ua_peer, fb_name, fb_type, 'ServiceInstanceSet', 'Instance')
                inst.parse_service_type_xml(instance_xml)
                # adds the method to the dict
                self.instances_dict[fb_name] = inst

    def from_fb(self, fb, fb_xml):
        # creates and parses the instance
        inst = ua_base.UaBaseLayer2(self.__ua_peer, fb.fb_name, fb.fb_type, 'ServiceInstanceSet', 'Instance')
        inst.parse_service_type_fb(fb, fb_xml)
        # adds the method to the dict
        self.instances_dict[fb.fb_name] = inst

    def save_xml(self, xml_set):
        # iterates over the instances of that service
        for instance_name, instance_item in self.instances_dict.items():
            # creates the instance xml
            instance_xml = ETree.SubElement(xml_set, 'serviceinstance')
            # saves the content of that instance
            instance_item.save_all_xml(instance_xml)
