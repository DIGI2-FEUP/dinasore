import importlib
import os
import sys
import xml.etree.ElementTree as ETree
import logging
from communication import marketplace_bridge
import threading
import time
import datetime
import subprocess



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
        fb_obj = None

        try:
            # Import method from python file
            importlib.invalidate_caches()
            py_fb = importlib.import_module('.' + self.fb_type, package='resources.function_blocks')
            # Gets the running fb method
            fb_class = getattr(py_fb, self.fb_type)
            # Instance the fb class
            fb_obj = fb_class()
            # Reads the xml
            tree = ETree.parse(self.fbt_path)
            # Gets the root element
            root = tree.getroot()

        except ModuleNotFoundError as error:
            logging.error('can not import the module (check fb_type.py nomenclature)')
            logging.error(error)
            logging.exception(error)

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

        return root, fb_obj

    def get_xml(self):
        logging.info('getting the xml fb definition...')
        root = None

        try:
            # Reads the xml
            tree = ETree.parse(self.fbt_path)
            # Gets the root element
            root = tree.getroot()
        except FileNotFoundError as error:
            logging.error('can not find the .fbt file (check .fbt name = fb_type.fbt)')
            logging.error(error)
        else:
            logging.info('fb definition (xml) imported from: {0}'.format(self.fbt_path))

        return root

    def get_description(self):
        xml_root = self.get_xml()

        # get the id and the type from the xml file
        for iterator in xml_root:
            if iterator.tag == 'SelfDescription':
                dev_id = iterator.attrib['ID']
                dev_type = iterator.attrib['FBType']

                return dev_id, dev_type

    def check_mp_fb(self):

        mp = marketplace_bridge.MarketplaceBridge

        # mp.checkFunctionBlock(self.fb_type,self.py_path,self.fbt_path)

        fbDetails = mp.getFbDetails(self.fb_type)
        if fbDetails['error'] == True:
            print('{} not found on markteplace'.format(self.fb_type))
            return
        
        self.fb_category = fbDetails['category']
        self.fb_dependencies = fbDetails['externalDependencies']
        self.installDependencies()

        exists_py = os.path.isfile(self.py_path) and False # Pendente de implementar versões
        exists_fbt = os.path.isfile(self.fbt_path) and False # Pendente de implementar versões

        if not exists_py or not exists_fbt:
            self.downloadFunctionBlocks()


    def installDependencies(self):
        for dependency in self.fb_dependencies:
            try:
                print('imported module {}',importlib.import_module(dependency['edName']))
            except ImportError:
                try:
                    print('Dependency {} not found, trying to install'.format(dependency))
                    # pipmain(['install',dependency['edName'],'--quiet','--user'])
                    subprocess.call(["pip", "install", dependency['edName']])
                except Exception:
                    print(Exception)
                    pass

    def downloadFunctionBlocks(self):
        mp = marketplace_bridge.MarketplaceBridge
        mp.downloadFunctionBlockFiles(self.fb_type,self.fb_category,self.py_path,self.fbt_path)


class GeneralResources:

    def __init__(self):
        # Gets the file path to the python file
        self.fb_path = os.path.join(os.path.dirname(sys.path[0]),
                                    'resources',
                                    'function_blocks')

    def list_existing_fb(self):
        only_files = []

        for f in os.listdir(self.fb_path):
            file_splitted = f.split('.')

            if os.path.isfile(os.path.join(self.fb_path, f)) and \
                    file_splitted[0] not in only_files and \
                    file_splitted[0] != '__init__':

                only_files.append(file_splitted[0])

        return only_files

    def search_description(self, dev_id):

        fb_types = self.list_existing_fb()

        for fb_type in fb_types:
            fb = FBResources(fb_type)
            # gets the device id and type
            dev_id_iterator, dev_type = fb.get_description()

            # compares if matches with the dev_id
            if dev_id == dev_id_iterator:
                return fb_type
