from communication import tcp_server
from core import manager
from tests import diac_simulator
from shutil import copyfile
from threading import Thread
from tests import base_dm
import os
import sys


class XMLTests(base_dm.BaseTests):
    file_name = 'tests_with_data.xml'
    # address = 'localhost'
    address = 'd_dinasore1'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

    def tearDown(self):
        self.manager_4diac.manager_ua.stop_ua()


class FBTests(base_dm.BaseTests):
    file_name = 'tests_no_data.xml'
    config2upload = 'full_config.fboot'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

        # creates the tcp server to communicate with the 4diac
        self.handler = tcp_server.TcpServer(self.address, 61499, 10, self.manager_4diac)
        # creates the handler
        thread = Thread(target=self.handler.handle_client)
        thread.start()

        # get the path for the config
        config_path = os.path.join(os.path.dirname(sys.path[0]),
                                   'tests',
                                   'configurations',
                                   self.config2upload)
        # sends the configuration to the
        sender_simulator = diac_simulator.DiacSimulator(self.address, 61499)
        sender_simulator.upload_dinasore(config_path)
        sender_simulator.disconnect()

    def tearDown(self):
        # stops the work at the
        self.manager_4diac.manager_ua.stop_ua()
        # stops the tcp server
        self.handler.stop_server()

        # gets  the path for the current data model and the clear copy
        original_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'tests_no_data.xml')
        backup_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model_copy.xml')
        # removes clears the file
        os.remove(original_file)
        # makes a copy of the backup file
        copyfile(backup_file, original_file)


class PermanentDataTest(base_dm.BaseTests):
    file_name = 'tests_no_data.xml'
    config2upload = 'full_config.fboot'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

        # creates the tcp server to communicate with the 4diac
        self.handler = tcp_server.TcpServer(self.address, 61499, 10, self.manager_4diac)
        # creates the handler
        thread = Thread(target=self.handler.handle_client)
        thread.start()

        # get the path for the config
        config_path = os.path.join(os.path.dirname(sys.path[0]),
                                   'tests',
                                   'configurations',
                                   self.config2upload)
        # sends the configuration to the
        sender_simulator = diac_simulator.DiacSimulator(self.address, 61499)
        sender_simulator.upload_dinasore(config_path)
        sender_simulator.disconnect()

        # stops the work at the
        self.manager_4diac.manager_ua.stop_ua()
        # stops the tcp server
        self.handler.stop_server()

        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

    def tearDown(self):
        # stops the work at the
        self.manager_4diac.manager_ua.stop_ua()

        # gets  the path for the current data model and the clear copy
        original_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'tests_no_data.xml')
        backup_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model_copy.xml')
        # removes clears the file
        os.remove(original_file)
        # makes a copy of the backup file
        copyfile(backup_file, original_file)


class FBPipelineTest(base_dm.PipelineTests):
    file_name = 'tests_no_data.xml'
    config2upload = 'pipeline_config.fboot'
    address = 'd_dinasore1'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

        # creates the tcp server to communicate with the 4diac
        self.handler = tcp_server.TcpServer(self.address, 61499, 10, self.manager_4diac)
        # creates the handler
        thread = Thread(target=self.handler.handle_client)
        thread.start()

        # get the path for the config
        config_path = os.path.join(os.path.dirname(sys.path[0]),
                                   'tests',
                                   'configurations',
                                   self.config2upload)
        # sends the configuration to the
        sender_simulator = diac_simulator.DiacSimulator(self.address, 61499)
        sender_simulator.upload_dinasore(config_path)
        sender_simulator.disconnect()

    def tearDown(self):
        # stops the work at the
        self.manager_4diac.manager_ua.stop_ua()
        # stops the tcp server
        self.handler.stop_server()

        # gets  the path for the current data model and the clear copy
        original_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'tests_no_data.xml')
        backup_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model_copy.xml')
        # removes clears the file
        os.remove(original_file)
        # makes a copy of the backup file
        copyfile(backup_file, original_file)


class PermanentPipelineTests(base_dm.PipelineTests):
    file_name = 'tests_no_data.xml'
    config2upload = 'pipeline_config.fboot'
    address = 'd_dinasore1'

    def setUp(self):
        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

        # creates the tcp server to communicate with the 4diac
        self.handler = tcp_server.TcpServer(self.address, 61499, 10, self.manager_4diac)
        # creates the handler
        thread = Thread(target=self.handler.handle_client)
        thread.start()

        # get the path for the config
        config_path = os.path.join(os.path.dirname(sys.path[0]),
                                   'tests',
                                   'configurations',
                                   self.config2upload)
        # sends the configuration to the
        sender_simulator = diac_simulator.DiacSimulator(self.address, 61499)
        sender_simulator.upload_dinasore(config_path)
        sender_simulator.disconnect()

        # stops the work at the
        self.manager_4diac.manager_ua.stop_ua()
        # stops the tcp server
        self.handler.stop_server()

        # creates the 4diac manager
        self.manager_4diac = manager.Manager()
        # creates the opc-ua manager
        self.manager_4diac.build_ua_manager(self.address, self.port_server, self.file_name)

    def tearDown(self):
        # stops the work at the
        self.manager_4diac.manager_ua.stop_ua()

        # gets  the path for the current data model and the clear copy
        original_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'tests_no_data.xml')
        backup_file = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'data_model_copy.xml')
        # removes clears the file
        os.remove(original_file)
        # makes a copy of the backup file
        copyfile(backup_file, original_file)
