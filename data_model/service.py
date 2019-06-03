from data_model import utils
from opcua import ua


class Service:

    def __init__(self, ua_peer):
        self.__ua_peer = ua_peer
        self.service_name, self.service_id = '', ''
        # key: constant_name, value: value to set (converted)
        self.constants = dict()
        self.subscriptions = dict()
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

        events to run method
            Run    (input_event)
            Run_O  (output_event)

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
        instance = InstanceService(self.__ua_peer, self)
        instance.from_xml(root_xml)
        # adds the method to the dict
        self.__instances[instance.instance_id] = instance

    def instance_from_ua(self, parent, *args):
        print('create instance')
        return []


class InstanceService:

    def __init__(self, ua_peer, service_base):
        self.__ua_peer = ua_peer
        self.service_base = service_base
        self.instance_id = ''

        # creates the path to the service set folder folder
        self.__INSTANCE_SET_LIST = self.__ua_peer.ROOT_LIST + [(2, 'ServiceInstanceSet')]
        self.__INSTANCE_SET_PATH = self.__ua_peer.generate_path(self.__INSTANCE_SET_LIST)

    def from_xml(self, root_xml):
        # gets the instance_id
        self.instance_id = root_xml.attrib['id']
        # creates the instance object
        instance_idx = 'ns=2;s={0}'.format(self.instance_id)
        obj_name = '{0}:{1}'.format(self.service_base.service_name, self.instance_id)
        instance_list, instance_path = utils.default_object(self.__ua_peer, instance_idx,
                                                            self.__INSTANCE_SET_PATH, self.__INSTANCE_SET_LIST,
                                                            obj_name)
        # creates the id and dId property
        utils.default_property(self.__ua_peer, instance_idx, instance_path, 'ID', self.instance_id)
        utils.default_property(self.__ua_peer, instance_idx, instance_path, 'dID', self.service_base.service_id)

        # creates the fb for the instance

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # creates the default methods 'AddLink', 'RemoveLink' and 'DeleteInstance'
            if tag == 'methods':
                # create the folder for the methods
                folder_idx, folder_path = utils.default_folder(self.__ua_peer,
                                                               instance_idx, instance_path, instance_list,
                                                               'Methods')
                for method in item:
                    if method.attrib['name'] == 'AddLink':
                        # creates the opc-ua method 'AddLink'
                        method_idx = '{0}:{1}'.format(folder_idx, 'AddLink')
                        browse_name = '2:{0}'.format('AddLink')
                        self.__ua_peer.create_method(folder_path,
                                                     method_idx,
                                                     browse_name,
                                                     self.add_ua_link,
                                                     input_args=[ua.VariantType.String],
                                                     output_args=[])

                    elif method.attrib['name'] == 'RemoveLink':
                        # creates the opc-ua method 'RemoveLink'
                        method_idx = '{0}:{1}'.format(folder_idx, 'RemoveLink')
                        browse_name = '2:{0}'.format('RemoveLink')
                        self.__ua_peer.create_method(folder_path,
                                                     method_idx,
                                                     browse_name,
                                                     self.remove_ua_link,
                                                     input_args=[ua.VariantType.String],
                                                     output_args=[])

                    elif method.attrib['name'] == 'DeleteInstance':
                        # creates the opc-ua method 'DeleteInstance'
                        method_idx = '{0}:{1}'.format(folder_idx, 'DeleteInstance')
                        browse_name = '2:{0}'.format('DeleteInstance')
                        self.__ua_peer.create_method(folder_path,
                                                     method_idx,
                                                     browse_name,
                                                     self.delete_ua,
                                                     input_args=[],
                                                     output_args=[])

            elif tag == 'subscriptions':
                pass

            elif tag == 'recipeadjustments':
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
