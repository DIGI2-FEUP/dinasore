from opcua import ua
import time
import unittest
from opc_ua import client
from opc_ua import handler
from opc_ua import peer
from opc_ua.examples import methods_example


class OpcUaTests(unittest.TestCase):
    # address = 'opc.tcp://localhost:4842'
    address = 'opc.tcp://d_dinasore1:4842'
    object_name = 'ExampleObject'
    var_name = 'ExampleVar'
    folder_name = 'ExampleFolder'
    property_name = 'ExampleProperty'
    method_name = 'hello_word'

    # address_auxiliary = 'opc.tcp://localhost:4841'
    address_auxiliary = 'opc.tcp://d_dinasore1:4841'

    def setUp(self):
        self.peer = peer.UaPeer(self.address)
        self.peer.create_object(2, self.object_name)
        object_path = self.peer.generate_path([(2, self.object_name)])
        self.peer.create_variable(object_path, 2, self.var_name, 6.01, True)
        self.peer.create_method(object_path,
                                2,
                                self.method_name,
                                methods_example.hello_word,
                                input_args=[ua.VariantType.String],
                                output_args=[ua.VariantType.Boolean])
        self.peer.create_folder(object_path, 2, self.folder_name)
        self.peer.create_property(object_path, 2, self.property_name, 'This is a property')

    def tearDown(self):
        self.peer.stop()

    def test_subscription(self):
        c = client.UaClient(self.address)

        variable_path = self.peer.generate_path([(2, self.object_name), (2, self.var_name)])
        c.subscribe(variable_path, handler.SubHandler())

        time.sleep(0.1)

        c.unsubscribe(variable_path)

        c.disconnect()

    def test_method(self):
        c = client.UaClient(self.address)

        method_path = self.peer.generate_path([(2, self.object_name), (2, self.method_name)])
        result = c.call_method(method_path.copy(), "World")
        self.assertEqual(True, result)

        result = c.call_method(method_path.copy(), "World")
        self.assertEqual(True, result)
        c.disconnect()

    def test_read(self):
        c = client.UaClient(self.address)

        path = self.peer.generate_path([(2, self.object_name), (2, self.var_name)])
        var = c.read(path)
        self.assertEqual(var, 6.01)

        c.disconnect()

    def test_write(self):
        c = client.UaClient(self.address)

        path = self.peer.generate_path([(2, self.object_name), (2, self.var_name)])
        c.write(path, 4.10)
        var = c.read(path)
        self.assertEqual(var, 4.10)

        c.disconnect()

    def test_add_clients(self):
        peer_aux = peer.UaPeer(self.address_auxiliary)

        peer_aux.add_client(self.address)
        self.peer.add_client(self.address_auxiliary)
        # self.peer.add_client(self.address_auxiliary)

        self.assertEqual(len(peer_aux.client_dictionary), 1)
        self.assertEqual(len(self.peer.client_dictionary), 1)

        peer_aux.remove_all_clients()
        self.peer.remove_all_clients()
        peer_aux.stop()

        self.assertEqual(len(peer_aux.client_dictionary), 0)
