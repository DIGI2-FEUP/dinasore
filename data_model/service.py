import xml.etree.ElementTree as ETree
from data_model import utils
from data_model import instance


class Service(utils.UaBaseStructure, utils.UaInterface):

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

            # parses the input/output variables
            if tag == 'interfaces':
                # parses the info from each interface
                for if_xml in item:
                    # gets the argument name and creates the folder
                    folder_name = if_xml.attrib['type']
                    # creates the variables arguments
                    if folder_name == 'Arguments':
                        # iterates over each variable
                        for var in if_xml[0]:
                            var_dict = dict()
                            # creates the variable
                            var_idx, var_object, var_path = self.create_xml_variable(var)
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

            # parses the constant variables
            elif tag == 'recipeadjustments':
                # iterate over each constant
                for rec_adj in item:
                    # iterates over each variable in the 'recipe adjustments'
                    for variable in rec_adj[0]:
                        var_dict = dict()
                        var_dict['Name'] = variable.attrib['name']
                        var_dict['DataType'] = variable.attrib['DataType']
                        var_dict['ValueRank'] = variable.attrib['ValueRank']
                        var_dict['Type'] = 'Constant'
                        self.variables_list.append(var_dict)

                        # creates the opc-ua variable
                        var_idx, var_object, var_path = self.create_xml_variable(variable)
                        # creates the respective property
                        utils.default_property(self.ua_peer, var_idx, var_path, 'Type', var_dict['Type'])

    def from_fb(self, input_vars_xml, output_vars_xml):
        # create the input variables interface
        for var_xml in input_vars_xml:
            var_idx, var_object, var_path = self.create_fb_variable(var_xml)
            # also creates the property
            utils.default_property(self.ua_peer, var_idx, var_path, 'Type', 'Output')
            # adds the variables to the list
            self.__create_var_entry('Input', var_xml)
        # create the output variables interface
        for var_xml in output_vars_xml:
            var_idx, var_object, var_path = self.create_fb_variable(var_xml)
            # also creates the property
            utils.default_property(self.ua_peer, var_idx, var_path, 'Type', 'Output')
            # adds the variables to the list
            self.__create_var_entry('Output', var_xml)

    def save_xml(self, service_xml):
        # sets the service xml attributes
        service_xml.attrib['dId'] = self.subs_id
        service_xml.attrib['name'] = self.subs_id
        # creates the recipe adjustment tag
        adj_xml = ETree.SubElement(service_xml, 'recipeadjustments')
        # creates the arguments tag
        interfaces_xml = ETree.SubElement(service_xml, 'interfaces')
        args_xml = ETree.SubElement(interfaces_xml, 'interface')
        args_xml.attrib['type'] = 'Arguments'
        vars_xml = ETree.SubElement(args_xml, 'variables')

        # iterates over each variable
        for var_item in self.variables_list:
            # recipe adjustment constant
            if var_item['Type'] == 'Constant':
                # creates the xml variable
                ra_xml = ETree.SubElement(adj_xml, 'recipeadjustment')
                ra_xml.attrib['name'] = var_item['Name']
                rav_xml = ETree.SubElement(ra_xml, 'variables')
                var_xml = ETree.SubElement(rav_xml, 'variable')
                var_xml.attrib['name'] = var_item['Name']
                var_xml.attrib['DataType'] = var_item['DataType']
                var_xml.attrib['ValueRank'] = var_item['ValueRank']

            # input/output variable
            else:
                # creates the xml variable
                var_xml = ETree.SubElement(vars_xml, 'variable')
                var_xml.attrib['name'] = var_item['Name']
                var_xml.attrib['DataType'] = var_item['DataType']
                var_xml.attrib['ValueRank'] = var_item['ValueRank']
                elements_xml = ETree.SubElement(var_xml, 'elements')
                ele_xml = ETree.SubElement(elements_xml, 'element')
                ele_xml.attrib = {'id': 'Type', 'DataType': 'String', 'ValueRank': '-1'}
                ele_xml.text = var_item['Type']

    def create_instance_from_xml(self, root_xml):
        # gets the instance_id
        subs_id = root_xml.attrib['id']
        fb_name = root_xml.attrib['id']
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self.subs_id, self.variables_list, subs_id, fb_name, self.fb_type)
        inst.from_xml(root_xml)
        # adds the method to the dict
        self.instances_dict[inst.subs_id] = inst

    def create_instance_from_fb(self, fb, fb_xml):
        # gets the instance_id
        subs_id = fb.fb_name
        fb_name = fb.fb_name
        fb_type = fb.fb_type
        # creates and parses the instance
        inst = instance.InstanceService(self.ua_peer, self.subs_id, self.variables_list, subs_id, fb_name, fb_type)
        inst.from_fb(fb, fb_xml)
        # adds the method to the dict
        self.instances_dict[inst.subs_id] = inst

    def __create_var_entry(self, var_type, var_xml):
        if var_xml.attrib['OpcUa'] == 'Variable':
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': var_type,
                        'DataType': utils.XML_4DIAC[var_xml.attrib['Type']],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)
        elif var_xml.attrib['OpcUa'] == 'Constant':
            # adds the variables to the list
            var_dict = {'Name': var_xml.attrib['Name'],
                        'Type': 'Constant',
                        'DataType': utils.XML_4DIAC[var_xml.attrib['Type']],
                        'ValueRank': '0'}
            self.variables_list.append(var_dict)

    def instance_from_ua(self, parent, *args):
        print('create instance')
        return []
