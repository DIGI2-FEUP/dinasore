from data_model import utils
from data_model import instance


class Service(utils.UaBaseStructure):

    def __init__(self, ua_peer):
        utils.UaBaseStructure.__init__(self, ua_peer, 'ServiceDescriptionSet')
        # key: constant_name, value: value to set (converted)
        self.variables_list = []
        # all instances from this service
        # key: instance_id, value: instance_obj
        self.instances_dict = dict()

    def from_xml(self, root_xml):
        self.fb_type = root_xml.attrib['name']
        self.subs_id = root_xml.attrib['dId']

        # creates the service
        self.create_base_object(browse_name=self.fb_type)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'methods':
                # sets the method 'CreateInstance'
                self.__create_methods()

            elif tag == 'interfaces':
                # parses the info from each interface
                self.__parse_variables(item)

    def from_fb(self, fb_type, fb_xml):
        self.fb_type = fb_type

        # parses the fb description
        fb_id, ua_type, input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = \
            self.parse_fb_description(fb_xml)
        self.subs_id = fb_id

        # creates the device object
        self.create_base_object(self.fb_type)

        # creates the methods
        self.__create_methods()

        # creates the interfaces folder
        folder_idx, ifs_path, ifs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                              self.base_path, self.base_path_list, 'Variables')
        # create the input variables interface
        for var_xml in input_vars_xml:
            self.create_fb_variable(var_xml, folder_idx, ifs_path)
            # adds the variables to the list
            self.__create_var_entry('Input', var_xml)
        # create the output variables interface
        for var_xml in output_vars_xml:
            self.create_fb_variable(var_xml, folder_idx, ifs_path)
            # adds the variables to the list
            self.__create_var_entry('Output', var_xml)

    def instance_from_xml(self, root_xml):
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self)
        inst.from_xml(root_xml)
        # adds the method to the dict
        self.instances_dict[inst.subs_id] = inst

    def instance_from_fb(self, fb, fb_xml):
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self)
        inst.from_fb(fb, fb_xml)
        # adds the method to the dict
        self.instances_dict[inst.subs_id] = inst

    def __create_methods(self):
        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                      self.base_path, self.base_path_list, 'Methods')
        # creates the opc-ua method
        method_idx = '{0}:{1}'.format(folder_idx, 'CreateInstance')
        self.ua_peer.create_method(methods_path, method_idx, '2:CreateInstance', self.instance_from_ua,
                                   input_args=[], output_args=[])

    def __parse_variables(self, ifs_xml):
        # creates the interfaces folder
        folder_idx, ifs_path, ifs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                              self.base_path, self.base_path_list, 'Variables')
        for if_xml in ifs_xml:
            # gets the argument name and creates the folder
            folder_name = if_xml.attrib['type']
            # creates the variables arguments
            if folder_name == 'Arguments':
                # iterates over each variable
                for var in if_xml[0]:
                    var_dict = dict()
                    # creates the variable
                    var_idx, var_object = self.create_variable(var, folder_idx, ifs_path)
                    var_path = self.ua_peer.generate_path(ifs_list + [(2, var.attrib['name'])])
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

    def __create_var_entry(self, var_type, var_xml):
        if var_xml.attrib['OpcUa'] == 'Variable':
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': var_type,
                        'DataType': var_xml.attrib['Type'],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)
        elif var_xml.attrib['OpcUa'] == 'Constant':
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': 'Constant',
                        'DataType': var_xml.attrib['Type'],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)

    def instance_from_ua(self, parent, *args):
        print('create instance')
        return []
