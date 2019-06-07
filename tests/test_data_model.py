from data_model import ua_manager
from core import manager
from opc_ua import client
import unittest


class DataModelTests(unittest.TestCase):
    port_server = 4841
    base_list = [(0, 'Objects'), (2, 'SmartObject')]

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_ua = ua_manager.UaManager('opc.tcp://localhost:{0}'.format(self.port_server),
                                               self.manager_4diac.set_config)
        self.manager_ua.from_xml()

    def tearDown(self):
        self.manager_ua.config.stop_work()
        self.manager_ua.stop()

    def test_fb_created(self):
        # check the number of fb
        n_fb = len(self.manager_ua.config.fb_dictionary)
        self.assertEqual(n_fb, 7)

    def test_device_set(self):
        c = client.UaClient('opc.tcp://localhost:{0}'.format(self.port_server))

        path = c.generate_path(self.base_list + [(2, 'DeviceSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 5)

        c.disconnect()

    def test_device_method(self):
        c = client.UaClient('opc.tcp://localhost:{0}'.format(self.port_server))

        method_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'DPFiltroCircuitoAgitação'),
                                                        (2, 'Methods'), (2, 'Calibrate')])
        var_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'DPFiltroCircuitoAgitação'),
                                                     (2, 'Variables'), (2, 'Pressure_1')])

        method_r = c.call_method(method_path.copy(), None)
        read_r = c.read(var_path)
        self.assertEqual(method_r, True)
        self.assertEqual(read_r, 3)

        method_r = c.call_method(method_path.copy(), None)
        read_r = c.read(var_path)
        self.assertEqual(method_r, True)
        self.assertEqual(read_r, 6)

        c.disconnect()

    def test_parse_service(self):
        pass

    def test_service_call(self):
        pass
