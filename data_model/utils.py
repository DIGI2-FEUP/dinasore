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


def default_folder(ua_peer, obj_idx, obj_path, path_list, obj_name, folder_name):
    # creates the methods folder
    folder_idx = '{0}:{1}'.format(obj_idx, folder_name)
    browse_name = '2:{0}'.format(folder_name)
    ua_peer.create_folder(obj_path, folder_idx, browse_name)
    # path for the methods folder
    folder_path = ua_peer.generate_path(path_list +
                                        [(2, obj_name), (2, folder_name)])
    return folder_idx, folder_path
