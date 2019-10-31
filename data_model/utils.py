from opcua import ua

UA_TYPES = {'String': ua.VariantType.String,
            'STRING': ua.VariantType.String,
            'Double': ua.VariantType.Double,
            'Integer': ua.VariantType.Int64,
            'INT': ua.VariantType.Int64,
            'UINT': ua.VariantType.UInt64,
            'Float': ua.VariantType.Float,
            'REAL': ua.VariantType.Float,
            'LREAL': ua.VariantType.Float,
            'BOOL': ua.VariantType.Boolean,
            'Boolean': ua.VariantType.Boolean}

XML_4DIAC = {'String': 'String',
             'STRING': 'String',
             'Double': 'Double',
             'Integer': 'Integer',
             'INT': 'Integer',
             'UINT': 'Integer',
             'Float': 'Float',
             'REAL': 'Float',
             'LREAL': 'Float',
             'BOOL': 'Boolean',
             'Boolean': 'Boolean'}

UA_NODE = {ua.VariantType.String: ua.NodeId(ua.ObjectIds.String),
           ua.VariantType.Double: ua.NodeId(ua.ObjectIds.Double),
           ua.VariantType.Int64: ua.NodeId(ua.ObjectIds.Int64),
           ua.VariantType.UInt64: ua.NodeId(ua.ObjectIds.UInt64),
           ua.VariantType.Float: ua.NodeId(ua.ObjectIds.Float),
           ua.VariantType.Boolean: ua.NodeId(ua.ObjectIds.Boolean)}

XML_NODE = {ua.ObjectIds.String: 'String',
            ua.ObjectIds.Double: 'Double',
            ua.ObjectIds.Int64: 'Integer',
            ua.ObjectIds.UInt64: 'Integer',
            ua.ObjectIds.Float: 'Float',
            ua.ObjectIds.Boolean: 'Boolean'}


def default_folder(ua_peer, obj_idx, obj_path, path_list, folder_name):
    # creates the methods folder
    folder_idx = '{0}:{1}'.format(obj_idx, folder_name)
    browse_name = '2:{0}'.format(folder_name)
    ua_peer.create_folder(obj_path, folder_idx, browse_name)
    # path for the methods folder
    folder_list = path_list + [(2, folder_name)]
    folder_path = ua_peer.generate_path(folder_list)
    return folder_idx, folder_path, folder_list


def default_property(ua_peer, obj_idx, obj_path, property_name, property_value):
    prop_idx = '{0}.{1}'.format(obj_idx, property_name)
    browse_name = '2:{0}'.format(property_name)
    ua_peer.create_property(obj_path, prop_idx, browse_name, property_value)


def default_object(ua_peer, obj_idx, obj_path, path_list, obj_name):
    browse_name = '2:{0}'.format(obj_name)
    ua_peer.create_object(obj_idx, browse_name, path=obj_path)
    # sets the path for the device object
    new_list = path_list + [(2, obj_name)]
    new_path = ua_peer.generate_path(new_list)
    return new_list, new_path


def parse_fb_description(fb_xml):
    input_events_xml, output_events_xml, input_vars_xml, output_vars_xml = None, None, None, None
    for item in fb_xml:
        # gets the events and vars
        if item.tag == 'InterfaceList':
            # Iterates over the interface list
            # to find the inputs/outputs
            for interface in item:
                # Input events
                if interface.tag == 'EventInputs':
                    input_events_xml = interface
                # Output events
                elif interface.tag == 'EventOutput':
                    output_events_xml = interface
                # Input variables
                elif interface.tag == 'InputVars':
                    input_vars_xml = interface
                # Output variables
                elif interface.tag == 'OutputVars':
                    output_vars_xml = interface

    return input_events_xml, output_events_xml, input_vars_xml, output_vars_xml


class UaInterface:

    def from_xml(self, item_xml):
        raise NotImplementedError

    def from_fb(self, fb, optional_fb_xml):
        raise NotImplementedError

    def save_xml(self, xml_set):
        raise NotImplementedError
