import threading
import pathlib
import datetime
import logging
import importlib
import sys, os

class Sniffer(threading.Thread):

    def __init__(self, ncap, fb_type, py_path, message_queue):
        threading.Thread.__init__(self, name=fb_type)
        self.alive = True
        self.fb_type = fb_type
        self.py_path = py_path
        self.message_queue = message_queue
        self.fname = pathlib.Path(self.py_path)
        if not self.fname.exists():
            logging.error('Could not find the file {0}'.format(self.py_path))
            sys.exit()
        else:
            # Get latest modification time to the file
            self.mtime = datetime.datetime.fromtimestamp(self.fname.stat().st_mtime)
            # Generate package path from py_path
            concatenate = False
            package = ''
            for dir in self.py_path.split(os.sep)[:-1]:
                if not concatenate:
                    if dir == 'resources':
                        concatenate = True
                if concatenate:
                    package += dir + '.'
            package = package[:-1]
            # Import method from python file
            self.py_fb = importlib.import_module('.' + self.fb_type, package=package)
            # Gets the running fb method
            fb_class = getattr(self.py_fb, self.fb_type)
            # Instantiate the fb class

            if(self.fb_type.find("IEEE1451") == 0):
                self.fb_obj = fb_class(ncap)
            else:
                self.fb_obj = fb_class()

    def run(self):        
        logging.info('Sniffer for {0} has been activated'.format(self.fb_type))
        while self.alive:
            nmtime = datetime.datetime.fromtimestamp(self.fname.stat().st_mtime)
            if nmtime > self.mtime:
                self.mtime = nmtime
                # Reloads imported module                
                importlib.reload(self.py_fb)
                # Gets the running fb method
                fb_class = getattr(self.py_fb, self.fb_type)
                # Instance the fb class
                self.fb_obj = fb_class()
                # Send new object to fb thread
                self.message_queue.put(self.fb_obj)
                logging.info('Changes to {0} detected, updating'.format(self.fb_type + '.py'))

    def kill(self):
        self.alive = False
