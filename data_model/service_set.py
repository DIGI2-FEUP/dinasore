from data_model import utils
from data_model import service


class Services:

    def __init__(self, ua_peer):
        # service_id: service
        self.service_dict = dict()
        # instance_id: service_id
        self.instances_map = dict()
        # receives the peer methods to add the opc-ua services
        self.__ua_peer = ua_peer

        # creates the service description opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'ServiceDescriptionSet')

        # creates the service instance opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'ServiceInstanceSet')

    def from_xml(self, xml_set):
        for service_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = service_xml.tag[1:].partition("}")

            if tag == 'servicedescription':
                s = service.Service(self.__ua_peer)
                s.from_xml(service_xml)

                # use the service_id as key
                self.service_dict[s.subs_id] = s

    def from_fb(self, fb_type, fb_xml):
        service_id, service_type = utils.read_description_from_fb(fb_xml)
        # checks if the service already exist in the service set
        if service_id not in self.service_dict:
            # otherwise it creates the service
            s = service.Service(self.__ua_peer)
            s.from_fb(fb_type, fb_xml)
            # use the service_id as key
            self.service_dict[s.subs_id] = s

    def instance_from_fb(self, fb, fb_xml):
        service_id, service_type = utils.read_description_from_fb(fb_xml)
        # get the service and create the instance
        s = self.service_dict[service_id]
        s.instance_from_fb(fb, fb_xml)
        # the instance_id is the same as the fb_name
        self.instances_map[fb.fb_name] = service_id

    def instances_from_xml(self, xml_set):
        for instance_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = instance_xml.tag[1:].partition("}")

            if tag == 'serviceinstance':
                # gets the service id
                service_id = instance_xml.attrib['dId']
                # gets the respective service from the dictionary
                s = self.service_dict[service_id]
                # parses the instance xml
                s.instance_from_xml(instance_xml)
                # connects the instance to the service
                instance_id = instance_xml.attrib['id']
                self.instances_map[instance_id] = service_id
