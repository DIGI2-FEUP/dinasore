import threading
import logging
from core import fb_interface


class FB(threading.Thread, fb_interface.FBInterface):

    def __init__(self, fb_name, fb_type, fb_exe, fb_xml):
        threading.Thread.__init__(self, name=fb_name)
        fb_interface.FBInterface.__init__(self, fb_name, fb_type, fb_xml)

        self.fb_exe = fb_exe
        self.kill_event = threading.Event()

    def run(self):
        logging.info('fb {0} started.'.format(self.fb_name))

        while not self.kill_event.is_set():

            self.wait_event()

            if self.kill_event.is_set():
                break

            inputs = self.read_inputs()

            logging.info('running fb...')

            try:
                outputs = self.fb_exe(*inputs)

            except TypeError as error:
                logging.error('invalid number of arguments (check if fb method args are in fb_type.fbt)')
                logging.exception(error)
                logging.error(error)
                # Stops the thread
                logging.info('stopping the fb work...')
                break

            except Exception as ex:
                logging.error(ex)
                logging.exception(ex)
                # Stops the thread
                logging.info('stopping the fb work...')
                break

            else:
                self.update_outputs(outputs)

    def stop(self):
        self.kill_event.set()
        self.new_event.set()

        logging.info('fb {0} stopped.'.format(self.fb_name))
