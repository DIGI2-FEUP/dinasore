from data_model import utils
from data_model import instance


class Service(utils.UaBaseStructure):

    def __init__(self, ua_peer):
        utils.UaBaseStructure.__init__(self, ua_peer, 'ServiceDescriptionSet')
        # key: constant_name, value: value to set (converted)
        self.variables_list = []
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
                self.__parse_recipe_adjustments(item)

            elif tag == 'methods':
                # sets the method 'CreateInstance'
                self.__parse_methods(item)

            elif tag == 'interfaces':
                # parses the info from each interface
                self.__parse_interfaces(item)

    def service_from_fb(self, fb, fb_xml):
        self.fb_type = fb.fb_type

        # parses the fb description
        ua_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
            self.parse_fb_description(fb_xml)

        # creates the device object
        self.create_base_object(self.fb_name)

        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                      self.base_path, self.base_path_list, 'Methods')
        # creates the create instance opc-ua method
        method_idx = '{0}:{1}'.format(folder_idx, 'CreateInstance')
        self.ua_peer.create_method(methods_path, method_idx, '2:CreateInstance', self.instance_from_ua,
                                   input_args=[], output_args=[])

        # creates the interfaces folder
        folder_idx, ifs_path, ifs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                              self.base_path, self.base_path_list, 'Interfaces')
        folder_idx, if_path, if_list = utils.default_folder(self.ua_peer, folder_idx,
                                                            ifs_path, ifs_list, 'Arguments')
        # create the input variables interface
        for var_xml in input_vars_xml:
            self.create_fb_variable(var_xml, folder_idx, if_path)
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': 'Input',
                        'DataType': var_xml.attrib['Type'],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)
        # create the output variables interface
        for var_xml in output_vars_xml:
            self.create_fb_variable(var_xml, folder_idx, if_path)
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': 'Output',
                        'DataType': var_xml.attrib['Type'],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)

    def __parse_methods(self, methods_xml):
        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                      self.base_path, self.base_path_list, 'Methods')
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

    def __parse_recipe_adjustments(self, adj_xml):
        # creates the Recipe Adjustments folder
        folder_idx, adjs_path, adjs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                self.base_path, self.base_path_list,
                                                                'RecipeAdjustments')

    def __parse_interfaces(self, ifs_xml):
        # creates the interfaces folder
        folder_idx, ifs_path, ifs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                              self.base_path, self.base_path_list, 'Interfaces')
        for if_xml in ifs_xml:
            # gets the argument name and creates the folder
            folder_name = if_xml.attrib['type']
            folder_idx, if_path, if_list = utils.default_folder(self.ua_peer, folder_idx,
                                                                ifs_path, ifs_list, folder_name)
            # creates the variables arguments
            if folder_name == 'Arguments':
                # iterates over each variable
                for var in if_xml[0]:
                    var_dict = dict()
                    # creates the variable
                    var_idx, var_object = self.create_variable(var, folder_idx, if_path)
                    var_path = self.ua_peer.generate_path(if_list + [(2, var.attrib['name'])])
                    # creates the type property
                    for ele in var[0]:
                        if ele.attrib['id'] == 'Type':
                            var_dict['Type'] = ele.text
                            utils.default_property(self.ua_peer, var_idx, var_path, 'Type', ele.text)

                    # add the var to the list
                    var_dict['Name'] = var.attrib['name']
                    var_dict['DataType'] = var.attrib['DataType']
                    var_dict['ValueRank'] = var.attrib['ValueRank']
                    self.variables_list.append(var_dict)

    def instance_from_xml(self, root_xml):
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self)
        inst.from_xml(root_xml)
        # adds the method to the dict
        self.__instances[inst.subs_id] = inst

    def instance_from_fb(self, fb, fb_xml):
        pass

    def get_instance(self, instance_id):
        if instance_id in self.__instances:
            return self.__instances[instance_id]
        else:
            return None

    def instance_from_ua(self, parent, *args):
        print('create instance')
        return []
