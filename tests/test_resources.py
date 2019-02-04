import unittest
import logging
from fb_management import fb_resources


class TestResources(unittest.TestCase):

    def setUp(self):
        # Configure the logging output
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s][%(levelname)s][%(threadName)-10s] %(message)s')

    def test_exists_fb(self):
        fb_res = fb_resources.FBResources('E_SWITCH')
        result = fb_res.exists_fb()
        self.assertEqual(True, result)

        fb_res = fb_resources.FBResources('E_SWITCH_1')
        result = fb_res.exists_fb()
        self.assertEqual(False, result)

    def test_import_fb(self):
        fb_res = fb_resources.FBResources('E_SWITCH')
        element, fb_exe = fb_res.import_fb()
        result = fb_exe(23, None)
        tag = element.tag
        self.assertEqual('FBType', tag)
        self.assertEqual(24, result[0])
