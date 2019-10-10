import xml.etree.ElementTree as ETree
from data_model import utils
from data_model import ua_base


class Service(ua_base.UaBaseStructure, utils.UaInterface):

    def __init__(self, ua_peer, fb_type):
        ua_base.UaBaseStructure.__init__(self, ua_peer, 'ServiceDescriptionSet',
                                         fb_name='Service:' + fb_type,
                                         fb_type=fb_type,
                                         browse_name=fb_type)

    def from_xml(self, root_xml):
        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            # parses the input/output variables
            if tag == 'variables':
                # link opc-ua variables in fb input variable
                # creates the opc-ua variables and links them
                for var in item:
                    # parses the variable
                    self.virtualize_variable(var)

    def from_fb(self, input_vars_xml, output_vars_xml):
        # create the input variables interface
        for var_xml in input_vars_xml:
            if 'OpcUa' in var_xml.attrib:
                var_specs = var_xml.attrib['OpcUa'].split('.')
                if ('Variable' in var_specs) or ('Constant' in var_specs):
                    self.virtualize_variable(var_xml)

        # create the input variables interface
        for var_xml in output_vars_xml:
            if 'OpcUa' in var_xml.attrib:
                var_specs = var_xml.attrib['OpcUa'].split('.')
                if ('Variable' in var_specs) or ('Constant' in var_specs):
                    self.virtualize_variable(var_xml)

    def save_xml(self, service_xml):
        # sets the service xml attributes
        service_xml.attrib['id'] = self.fb_type
        service_xml.attrib['type'] = 'service'

        vars_xml = ETree.SubElement(service_xml, 'variables')
        # iterates over each variable
        self.save_variables(vars_xml)
