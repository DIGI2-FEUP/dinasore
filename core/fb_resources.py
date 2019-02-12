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
        root = None
        fb_exe = None

        try:
            # Import method from python file
            py_fb = importlib.import_module('.' + self.fb_type, package='resources.function_blocks')
            # Gets the running fb method
            fb_class = getattr(py_fb, self.fb_type)
            # Instance the fb class
            instance = fb_class()
            # Gets the fb schedule method
            fb_exe = instance.schedule
            # Reads the xml
            tree = ETree.parse(self.fbt_path)
            # Gets the root element
            root = tree.getroot()

        except ModuleNotFoundError as error:
            logging.error('can not import the module (check fb_type.py nomenclature)')
            logging.error(error)

        except AttributeError as error:
            logging.error('can not find the fb method declaration (check if fb_type.py = def fb_type(...):)')
            logging.error(error)

        except FileNotFoundError as error:
            logging.error('can not find the .fbt file (check .fbt name = fb_type.fbt)')
            logging.error(error)

        except Exception as ex:
            logging.error(ex)

        else:
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
