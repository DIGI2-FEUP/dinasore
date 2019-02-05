import unittest
import os
import sys
from xml.etree import ElementTree as ETree
from core import manager


class TestParse(unittest.TestCase):

    def setUp(self):
        # Gets the file path to the configuration request (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'configuration_request.xml')
        tree = ETree.parse(path)
        self.config_request = ETree.tostring(tree.getroot(), encoding='utf-8')

        # Gets the file path to the fb request (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'fb_request.xml')
        tree = ETree.parse(path)
        self.fb_request = ETree.tostring(tree.getroot(), encoding='utf-8')

        # Gets the file path to the watch create (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'watch_create.xml')
        tree = ETree.parse(path)
        self.watch_create = ETree.tostring(tree.getroot(), encoding='utf-8')

        # Gets the file path to the watch request (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'watch_request.xml')
        tree = ETree.parse(path)
        self.watch_request = ETree.tostring(tree.getroot(), encoding='utf-8')

        # Gets the file path to the watch response (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'event_request.xml')
        tree = ETree.parse(path)
        self.event_request = ETree.tostring(tree.getroot(), encoding='utf-8')

        # Gets the file path to the hardcoded connection (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'hardcoded_connection.xml')
        tree = ETree.parse(path)
        self.hardcoded_connection = ETree.tostring(tree.getroot(), encoding='utf-8')

        # Gets the file path to the connection request (xml) file
        path = os.path.join(os.path.dirname(sys.path[0]), 'tests', 'xml_data', 'connection_request.xml')
        tree = ETree.parse(path)
        self.connection_request = ETree.tostring(tree.getroot(), encoding='utf-8')

        self.manager_instance = manager.Manager()

    def test_configuration(self):
        response = self.manager_instance.parse_general(self.config_request)

        self.assertEqual(b'P\x00\x13<Response ID="1" />', response)
        self.assertEqual(1, len(self.manager_instance.config_dictionary))

    def test_fb(self):
        self.manager_instance.parse_general(self.config_request)

        response = self.manager_instance.parse_configuration(self.fb_request, 'EMB_RES')
        fb = self.manager_instance.config_dictionary['EMB_RES'].fb_dictionary['E_EXAMPLE_1']

        self.assertEqual(b'P\x00\x13<Response ID="2" />', response)
        self.assertEqual(1, len(fb.input_events))
        self.assertEqual(2, len(fb.output_events))
        self.assertEqual(1, len(fb.input_vars))
        self.assertEqual(0, len(fb.output_vars))
        self.assertEqual(1, len(fb.input_events))

    def test_create_watch(self):
        self.manager_instance.parse_general(self.config_request)
        self.manager_instance.parse_configuration(self.fb_request, 'EMB_RES')

        response = self.manager_instance.parse_configuration(self.watch_create, 'EMB_RES')

        self.assertEqual(b'P\x00\x13<Response ID="3" />', response)

    def test_event(self):
        self.manager_instance.parse_general(self.config_request)
        self.manager_instance.parse_configuration(self.fb_request, 'EMB_RES')

        response = self.manager_instance.parse_configuration(self.event_request, 'EMB_RES')

        self.assertEqual(b'P\x00\x13<Response ID="4" />', response)

    def test_watch(self):
        self.manager_instance.parse_general(self.config_request)
        self.manager_instance.parse_configuration(self.fb_request, 'EMB_RES')
        self.manager_instance.parse_configuration(self.watch_create, 'EMB_RES')
        self.manager_instance.parse_configuration(self.event_request, 'EMB_RES')

        response = self.manager_instance.parse_general(self.watch_request)

        self.assertEqual(b'P\x00\xa2<Response ID="5"><Watches><Resource name="EMB_RES"><FB name="E_EX'
                         b'AMPLE_1"><Port name="EO0"><Data time="',
                         response[0:106])

        self.assertEqual(b'" value="1" /></Port></FB></Resource></Watches></Response>', response[107:])

    def test_hardcoded_connection(self):
        self.manager_instance.parse_general(self.config_request)
        self.manager_instance.parse_configuration(self.fb_request, 'EMB_RES')
        response = self.manager_instance.parse_configuration(self.hardcoded_connection, 'EMB_RES')

        self.assertEqual(b'P\x00\x13<Response ID="6" />', response)

        fb = self.manager_instance.config_dictionary['EMB_RES'].fb_dictionary['E_EXAMPLE_1']
        v_type, value, is_watch = fb.read_attr('G')
        self.assertEqual('true', value)

    def test_connection(self):
        self.manager_instance.parse_general(self.config_request)
        self.manager_instance.parse_configuration(self.fb_request, 'EMB_RES')
        response = self.manager_instance.parse_configuration(self.connection_request, 'EMB_RES')

        self.assertEqual(b'P\x00\x13<Response ID="7" />', response)

        fb = self.manager_instance.config_dictionary['EMB_RES'].fb_dictionary['E_EXAMPLE_1']
        self.assertEqual(1, len(fb.output_connections))





