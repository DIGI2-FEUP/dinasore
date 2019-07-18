from data_model import device
from data_model import utils
import xml.etree.ElementTree as ETree


class Point(device.Device):

    def __init__(self, ua_peer, subs_id, fb_name, fb_type, point_type):
        device.Device.__init__(self, ua_peer, subs_id, fb_name, fb_type, 'RUNNING', 'PointSet')
        # set the fb general type to start point aka device type
        self.fb_general_type = point_type

    def save_xml(self, point_xml):
        point_xml.attrib['dId'] = self.subs_id
        point_xml.attrib['name'] = self.fb_name
        point_xml.attrib['type'] = self.fb_type

        # creates the variables xml
        variables_xml = ETree.SubElement(point_xml, 'variables')

        # gets the variables object
        vars_object = self.ua_peer.get_object(self.vars_path)
        children = vars_object.get_children()
        for child in children:
            # creates each variables
            var_xml = ETree.SubElement(variables_xml, 'variable')
            var_xml.attrib = {'name': child.get_display_name().to_string(),
                              'DataType': utils.XML_TYPES[child.get_data_type_as_variant_type()],
                              'ValueRank': str(child.get_value_rank())}

        # creates the methods xml
        methods_xml = ETree.SubElement(point_xml, 'methods')
        # iterates over each method
        for method_name, ua_method in self.ua_methods.items():
            # creates the xml method
            method_xml = ETree.SubElement(methods_xml, 'method')
            # saves the method inside the xml
            ua_method.save_xml(method_xml)

        # saves the subscriptions
        subscriptions_xml = ETree.SubElement(point_xml, 'subscriptions')
        # saves the constant values
        for variable_item in self.variables_list:
            # checks if is a constant
            if variable_item['Type'] == 'Constant':
                # creates the constant xml
                subs_xml = ETree.SubElement(subscriptions_xml, 'id')
                subs_xml.attrib['BrowseDirection'] = 'both'
                subs_xml.attrib['type'] = 'Data'
                subs_xml.attrib['VariableName'] = variable_item['Name']
                var_ref = self.ua_peer.get_node('ns=2;s={0}:Variables:{1}'.format(self.subs_id, variable_item['Name']))
                subs_xml.text = str(var_ref.get_value())

        # also saves the connections
        if self.fb_general_type == 'ENDPOINT':
            # iterates over the subscriptions
            for subs_name, subs_value in self.subscriptions_dict.items():
                # creates the subscription
                subs_xml = ETree.SubElement(subscriptions_xml, 'id')
                subs_xml.attrib['BrowseDirection'] = 'forward'
                subs_xml.attrib['type'] = 'Data'
                subs_xml.attrib['VariableName'] = subs_name

                # gets the node_id
                node_id = None
                for item in subs_value.nodeid.to_string().split(';'):
                    if item[:2] == 's=':
                        node_id = item[2:]
                subs_xml.text = node_id
