from data_model import utils


class Service:

    def __init__(self, ua_peer):
        self.__ua_peer = ua_peer
        self.service_name, self.service_id = '', ''
        # all instances from this service
        # key: instance_id, value: instance_obj
        self.__instances = dict()

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
        self.service_name = root_xml.attrib['name']
        self.service_id = root_xml.attrib['dId']

        # creates the service
        service_idx = 'ns=2;s={0}'.format(self.service_id)
        service_list, service_path = utils.default_object(self.__ua_peer, service_idx,
                                                          self.__SERVICE_SET_PATH, self.__SERVICE_SET_LIST,
                                                          obj_name=self.service_name)
        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # sets the constant variables values
            if tag == 'recipeadjustments':
                # creates the Recipe Adjustments folder
                folder_idx, adjustments_path = utils.default_folder(self.__ua_peer,
                                                                    service_idx, service_path, service_list,
                                                                    'RecipeAdjustments')

            # sets the method 'CreateInstance'
            elif tag == 'methods':
                # creates the methods folder
                folder_idx, methods_path = utils.default_folder(self.__ua_peer,
                                                                service_idx, service_path, service_list,
                                                                'Methods')
                # creates each different method
                for method_xml in item:
                    # case method create instance
                    if method_xml.attrib['name'] == 'CreateInstance':
                        # creates the opc-ua method
                        method_idx = '{0}:{1}'.format(folder_idx, 'CreateInstance')
                        self.__ua_peer.create_method(methods_path,
                                                     method_idx,
                                                     '2:CreateInstance',
                                                     self.instance_from_ua,
                                                     input_args=[],
                                                     output_args=[])

            # parses the info from each interface
            elif tag == 'interfaces':
                # creates the interfaces folder
                folder_idx, interfaces_path = utils.default_folder(self.__ua_peer,
                                                                   service_idx, service_path, service_list,
                                                                   'Interfaces')

    def instance_from_xml(self, root_xml):
        # creates and parses the instance
        instance = InstanceService(self.__ua_peer)
        instance.from_xml(root_xml)
        # adds the method to the dict
        self.__instances[instance.instance_id] = instance

    def instance_from_ua(self, parent, *args):
        print('create instance')
        return []


class InstanceService:

    def __init__(self, ua_peer):
        self.__ua_peer = ua_peer
        self.instance_id = ''

        # creates the path to the service set folder folder
        self.__INSTANCE_SET_LIST = self.__ua_peer.ROOT_LIST + [(2, 'ServiceInstanceSet')]
        self.__INSTANCE_SET_PATH = self.__ua_peer.generate_path(self.__INSTANCE_SET_LIST)

    def from_xml(self, root_xml):
        # gets the instance_id
        self.instance_id = root_xml.attrib['id']

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # creates the default methods 'AddLink', 'RemoveLink' and 'DeleteInstance'
            if tag == 'methods':
                pass

            elif tag == 'subscriptions':
                pass

            elif tag == 'recipeadjustments':
                pass

    def add_ua_link(self):
        pass

    def remove_ua_link(self):
        pass
