from opc_ua import client
from opc_ua import peer
from opcua import ua
import logging


def get_node(base_obj):
    print(base_obj)
    children = base_obj.get_children()
    for child in children:
        print(child.get_value())
        get_node(child)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')
    client_opc = client.UaClient('opc.tcp://localhost:4841')
    path = client_opc.generate_path([(0, 'Objects'), (2, 'SMART_COMPONENT'), (2, 'ServiceInstanceSet'),
                                     (2, 'SERVICE_EXAMPLE_1'), (2, 'Variables')])
    objects_node = client_opc.get_object(path)
    client_opc.get_objects_node()
    get_node(objects_node)
    client_opc.disconnect()

# Node(StringNodeId(ns=2;s=SERVICE_EXAMPLE_1:Variables:RATE))
# Node(StringNodeId(ns=2;s=SERVICE_EXAMPLE_1:Variables:RATE))

    # ua_peer = peer.UaPeer('opc.tcp://localhost:4841')
    # ua_peer.create_object('ns=2;s=Example1', '2:Example1')
    # ua_peer.create_object(2, 'Example2')
    # object_path_1 = ua_peer.generate_path([(2, 'Example1')])
    # object_path_2 = ua_peer.generate_path([(2, 'Example2')])
    # ua_peer.create_folder(object_path_2, 2, 'Folder1')
    # folder_path = ua_peer.generate_path([(2, 'Example2'), (2, 'Folder1')])
    #
    # folder = ua_peer.get_object(folder_path)
    # example_1 = ua_peer.get_node('ns=2;s=Example1')
    # folder.add_reference(example_1, ua.ObjectIds.Organizes)
    # children = folder.get_children()
    # print(children)
