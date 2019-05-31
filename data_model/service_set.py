from data_model import utils
from data_model import service


class Services:

    def __init__(self, ua_peer):
        self.__service_set = dict()
        # receives the peer methods to add the opc-ua services
        self.__ua_peer = ua_peer

        # creates the service description opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST,
                             'ServiceDescriptionSet')

        # creates the service instance opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST,
                             'ServiceInstanceSet')

    def services_from_xml(self, xml_set):
        for service_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = service_xml.tag[1:].partition("}")

            if tag == 'servicedescription':
                s = service.Service(self.__ua_peer)
                s.service_from_xml(service_xml)

                # use the service_id as key
                self.__service_set[s.service_id] = s

    def instances_from_xml(self, xml_set):
        for instance_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = instance_xml.tag[1:].partition("}")

            if tag == 'serviceinstance':
                # gets the service id
                service_id = instance_xml.attrib['dId']
                # gets the respective service from the dictionary
                s = self.__service_set[service_id]
                # parses the instance xml
                s.instance_from_xml(instance_xml)

    def services_from_diac(self, xml_set):
        pass

    def instances_from_diac(self, xml_set):
        pass
