from communication import tcp_server
from core import manager
from opc_ua import client
from tests import diac_simulator
from shutil import copyfile
from threading import Thread
import unittest
import os
import sys


class DataModelTests(unittest.TestCase):
    port_server = 4841
    base_name = 'SMART_OBJECT'
    base_list = [(0, 'Objects'), (2, base_name)]
    file_name = 'tests_with_data.xml'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.base_name, '0.0.0.0', self.port_server, self.file_name)

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


class ParseTests(unittest.TestCase):
    port_server = 4841
    base_name = 'SMART_COMPONENT'
    base_list = [(0, 'Objects'), (2, base_name)]
    file_name = 'tests_no_data.xml'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.base_name, '0.0.0.0', self.port_server, self.file_name)

        # creates the tcp server to communicate with the 4diac
        self.handler = tcp_server.TcpServer('0.0.0.0', 61499, 10, self.manager_4diac)
        # creates the handler
        thread = Thread(target=self.handler.handle_client)
        thread.start()

        # stop the manager
        self.manager_4diac.parse_general('<Request ID="0" Action="KILL">'
                                         '<FB Name="SMART_COMPONENT" Type=""/></Request>')
        self.manager_4diac.parse_general('<Request ID="1" Action="DELETE">'
                                         '<FB Name="SMART_COMPONENT" Type=""/></Request>')

        # get the path for the config
        config_path = os.path.join(os.path.dirname(sys.path[0]),
                                   'tests',
                                   'configurations',
                                   'opc_ua_FORTE_PC.fboot')
        # sends the configuration to the
        sender_simulator = diac_simulator.DiacSimulator('0.0.0.0', 61499)
        sender_simulator.upload_dinasore(config_path)
        sender_simulator.disconnect()

    def tearDown(self):
        # stops the work at the
        self.manager_4diac.manager_ua.config.stop_work()
        self.manager_4diac.manager_ua.stop()
        # stops the tcp server
        self.handler.stop_server()

        # gets  the path for the current data model and the clear copy
        original_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'tests_no_data.xml')
        backup_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model_copy.xml')
        # removes clears the file
        os.remove(original_file)
        # makes a copy of the backup file
        copyfile(backup_file, original_file)

    def test_opc_server(self):
        c = client.UaClient('opc.tcp://0.0.0.0:{0}'.format(self.port_server))

        path = c.generate_path(self.base_list + [(2, 'ServiceDescriptionSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 1)

        path = c.generate_path(self.base_list + [(2, 'DeviceSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 3)

        path = c.generate_path(self.base_list + [(2, 'PointSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 0)

        c.disconnect()
