from opcua import ua

UA_TYPES = {'String': ua.VariantType.String,
            'Double': ua.VariantType.Double,
            'Integer': ua.VariantType.Int64,
            'Float': ua.VariantType.Float,
            'Boolean': ua.VariantType.Boolean}

UA_RANKS = {'1': ua.ValueRank.OneDimension,
            '0': ua.ValueRank.OneOrMoreDimensions,
            '-1': ua.ValueRank.Scalar,
            '-2': ua.ValueRank.Any,
            '-3': ua.ValueRank.ScalarOrOneDimension}


def default_folder(ua_peer, obj_idx, obj_path, path_list, folder_name):
    # creates the methods folder
    folder_idx = '{0}:{1}'.format(obj_idx, folder_name)
    browse_name = '2:{0}'.format(folder_name)
    ua_peer.create_folder(obj_path, folder_idx, browse_name)
    # path for the methods folder
    folder_path = ua_peer.generate_path(path_list + [(2, folder_name)])
    return folder_idx, folder_path


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


class DiacInterface:

    def __init__(self, ua_peer, folder_name):
        self.fb_name, self.fb_type = None, None
        self.subs_id = None
        self.base_idx, self.base_path, self.base_path_list = None, None, None
        self.ua_peer = ua_peer
        self.folder_name = folder_name

    def create_base_object(self, browse_name):
        # creates the path to set the folder
        folder_path_list = self.ua_peer.ROOT_LIST + [(2, self.folder_name)]
        folder_path = self.ua_peer.generate_path(folder_path_list)

        self.base_idx = 'ns=2;s={0}'.format(self.subs_id)
        # creates the device object
        self.base_path_list, self.base_path = default_object(self.ua_peer, self.base_idx,
                                                             folder_path, folder_path_list,
                                                             browse_name)
