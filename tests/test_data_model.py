from core import manager
from core import configuration
from opc_ua import client
import unittest


class DataModelTests(unittest.TestCase):
    port_server = 4841
    base_name = 'SMART_OBJECT'
    base_list = [(0, 'Objects'), (2, base_name)]
    file_name = 'data_model_original.xml'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        config = configuration.Configuration(self.base_name, 'EMB_RES')
        self.manager_4diac.set_config(self.base_name, config)
        self.manager_4diac.build_ua_manager(self.base_name, '0.0.0.0', 4841, self.file_name)

    def tearDown(self):
        self.manager_4diac.manager_ua.config.stop_work()
        self.manager_4diac.manager_ua.stop()

    def test_fb_created(self):
        # check the number of fb
        n_fb = len(self.manager_4diac.manager_ua.config.fb_dictionary)
        self.assertEqual(n_fb, 8)

    def test_device_set(self):
        c = client.UaClient('opc.tcp://0.0.0.0:{0}'.format(self.port_server))

        path = c.generate_path(self.base_list + [(2, 'DeviceSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 3)

        c.disconnect()

    def test_device_method(self):
        c = client.UaClient('opc.tcp://0.0.0.0:{0}'.format(self.port_server))

        method_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PRESSURE_SENSOR_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        var_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PRESSURE_SENSOR_1'),
                                                     (2, 'Variables'), (2, 'PRESSURE')])

        method_r = c.call_method(method_path.copy(), None)
        read_r = c.read(var_path)
        self.assertEqual(method_r, [False])
        self.assertEqual(read_r, 0)

        method_r = c.call_method(method_path.copy(), None)
        read_r = c.read(var_path)
        self.assertEqual(method_r, [False])
        self.assertEqual(read_r, 0)

        c.disconnect()

    def test_service_set(self):
        c = client.UaClient('opc.tcp://0.0.0.0:{0}'.format(self.port_server))

        path = c.generate_path(self.base_list + [(2, 'ServiceDescriptionSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 1)

        c.disconnect()
