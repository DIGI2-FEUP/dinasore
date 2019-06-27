from data_model import ua_manager
from core import manager
from core import configuration
from opc_ua import client
import unittest


class DataModelTests(unittest.TestCase):
    port_server = 4841
    base_name = 'SmartObject'
    base_list = [(0, 'Objects'), (2, base_name)]

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        config = configuration.Configuration(self.base_name, 'EMB_RES')
        self.manager_4diac.set_config(self.base_name, config)
        self.manager_ua = ua_manager.UaManager(self.base_name, 'opc.tcp://localhost:{0}'.format(self.port_server),
                                               config, 'data_model_original.xml')
        self.manager_ua.from_xml()

    def tearDown(self):
        self.manager_ua.config.stop_work()
        self.manager_ua.stop()

    def test_fb_created(self):
        # check the number of fb
        n_fb = len(self.manager_ua.config.fb_dictionary)
        self.assertEqual(n_fb, 8)

    def test_device_set(self):
        c = client.UaClient('opc.tcp://localhost:{0}'.format(self.port_server))

        path = c.generate_path(self.base_list + [(2, 'DeviceSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 3)

        c.disconnect()

    def test_device_method(self):
        c = client.UaClient('opc.tcp://localhost:{0}'.format(self.port_server))

        method_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'TTS - Tina 1'),
                                                        (2, 'Methods'), (2, 'Calibrate')])
        var_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'TTS - Tina 0'),
                                                     (2, 'Variables'), (2, 'Pressure')])

        method_r = c.call_method(method_path.copy(), None)
        read_r = c.read(var_path)
        self.assertEqual(method_r, True)
        self.assertEqual(read_r, 0)

        method_r = c.call_method(method_path.copy(), None)
        read_r = c.read(var_path)
        self.assertEqual(method_r, True)
        self.assertEqual(read_r, 0)

        c.disconnect()

    def test_parse_service(self):
        pass

    def test_service_call(self):
        pass
