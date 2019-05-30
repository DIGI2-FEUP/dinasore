

class Services:

    def __init__(self, ua_peer):
        self.__service_set = dict()
        self.__service_instances = dict()
        # receives the peer methods to add the opc-ua services
        self.__ua_peer = ua_peer

        # creates the service description opc-ua folder
        idx = 'ns=2;s={0}:{1}'.format(self.__ua_peer.idx, 'ServiceDescriptionSet')
        self.__ua_peer.create_folder(self.__ua_peer.ROOT_PATH, idx, '2:ServiceDescriptionSet')

        # creates the service instance opc-ua folder
        idx = 'ns=2;s={0}:{1}'.format(self.__ua_peer.idx, 'ServiceInstanceSet')
        self.__ua_peer.create_folder(self.__ua_peer.ROOT_PATH, idx, '2:ServiceInstanceSet')

    def services_from_xml(self, xml_set):
        for service_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = service_xml.tag[1:].partition("}")

            if tag == 'servicedescription':
                service = Service(self.__ua_peer)
                service.service_from_xml(service_xml)

                # use the fb_name as key
                # self.__service_set[] = dev

    def instances_from_xml(self, xml_set):
        for instance_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = instance_xml.tag[1:].partition("}")

            if tag == 'serviceinstance':
                pass

    def services_from_diac(self, xml_set):
        pass

    def instances_from_diac(self, xml_set):
        pass


class Service:

    def __init__(self, ua_peer):
        self.__ua_peer = ua_peer

        # creates the path to the service set folder folder
        self.__SERVICE_SET_LIST = self.__ua_peer.ROOT_LIST + [(2, 'ServiceDescriptionSet')]
        self.__SERVICE_SET_PATH = self.__ua_peer.generate_path(self.__SERVICE_SET_LIST)

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
        :param root_xml:
        """
        pass

    def instance_from_xml(self, root_xml):

        def add_instance(parent):
            pass
