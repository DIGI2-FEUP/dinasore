from data_model import utils
from data_model import instance


class Service(utils.UaBaseStructure):

    def __init__(self, ua_peer, subs_id, fb_name, fb_type):
        utils.UaBaseStructure.__init__(self, ua_peer, 'ServiceDescriptionSet',
                                       subs_id=subs_id,
                                       fb_name=fb_name,
                                       fb_type=fb_type,
                                       browse_name=fb_type)
        # key: constant_name, value: value to set (converted)
        self.variables_list = []
        # all instances from this service
        # key: instance_id, value: instance_obj
        self.instances_dict = dict()

        # sets the method 'CreateInstance'
        # creates the opc-ua method
        method_idx = '{0}:{1}'.format(self.methods_idx, 'CreateInstance')
        self.ua_peer.create_method(self.methods_path, method_idx, '2:CreateInstance', self.instance_from_ua,
                                   input_args=[], output_args=[])

    def from_xml(self, root_xml):
        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'interfaces':
                # parses the info from each interface
                self.__parse_variables(item)

    def from_fb(self, input_vars_xml, output_vars_xml):
        # create the input variables interface
        for var_xml in input_vars_xml:
            self.create_fb_variable(var_xml)
            # adds the variables to the list
            self.__create_var_entry('Input', var_xml)
        # create the output variables interface
        for var_xml in output_vars_xml:
            self.create_fb_variable(var_xml)
            # adds the variables to the list
            self.__create_var_entry('Output', var_xml)

    def create_instance_from_xml(self, root_xml):
        # gets the instance_id
        subs_id = root_xml.attrib['id']
        fb_name = root_xml.attrib['id']
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self.subs_id, self.variables_list, subs_id, fb_name, self.fb_type)
        inst.from_xml(root_xml)
        # adds the method to the dict
        self.instances_dict[inst.subs_id] = inst

    def create_instance_from_fb(self, fb):
        # gets the instance_id
        subs_id = fb.fb_name
        fb_name = fb.fb_name
        fb_type = fb.fb_type
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self.subs_id, self.variables_list, subs_id, fb_name, fb_type)
        inst.from_fb(fb)
        # adds the method to the dict
        self.instances_dict[inst.subs_id] = inst

    def __parse_variables(self, ifs_xml):
        for if_xml in ifs_xml:
            # gets the argument name and creates the folder
            folder_name = if_xml.attrib['type']
            # creates the variables arguments
            if folder_name == 'Arguments':
                # iterates over each variable
                for var in if_xml[0]:
                    var_dict = dict()
                    # creates the variable
                    var_idx, var_object = self.create_xml_variable(var)
                    var_path = self.ua_peer.generate_path(self.vars_list + [(2, var.attrib['name'])])
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
