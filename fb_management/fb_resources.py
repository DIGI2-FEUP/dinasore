import importlib
import os
import sys
import xml.etree.ElementTree as ETree
import logging


class FBResources:

    def __init__(self, fb_type):
        self.fb_type = fb_type

        # Gets the file path to the python file
        self.py_path = os.path.join(os.path.dirname(sys.path[0]),
                                    'resources',
                                    'function_blocks',
                                    fb_type + '.py')

        # Gets the file path to the fbt (xml) file
        self.fbt_path = os.path.join(os.path.dirname(sys.path[0]),
                                     'resources',
                                     'function_blocks',
                                     fb_type + '.fbt')

    def import_fb(self):
        logging.info('importing fb python file and definition file...')

        # Import method from python file
        py_fb = importlib.import_module('.' + self.fb_type, package='resources.function_blocks')
        # Reloads the module if it was changed
        importlib.reload(py_fb)
        # Gets the running fb method
        fb_exe = getattr(py_fb, self.fb_type)

        # Reads the xml
        tree = ETree.parse(self.fbt_path)
        # Gets the root element
        root = tree.getroot()

        logging.info('fb definition (xml) imported from: {0}'.format(self.fbt_path))
        logging.info('python file imported from: {0}'.format(self.py_path))

        return root, fb_exe

    def exists_fb(self):
        # Verifies if exists the python file
        exists_py = os.path.isfile(self.py_path)
        # Verifies if exists the fbt file
        exists_fbt = os.path.isfile(self.fbt_path)

        if exists_py and exists_fbt:
            return True
        else:
            return False

    def download_fb(self):
        pass

    def exists_module(self, mod_id):
        pass

    def download_module(self, mod_id):
        pass
