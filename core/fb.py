import threading
import logging
from core import fb_interface
from core import sniffer
import os
from data_model_fboot import utils
import queue

class FB(threading.Thread, fb_interface.FBInterface):

    def __init__(self, fb_name, fb_type, fb_obj, fb_xml, monitor=None):
        threading.Thread.__init__(self, name=fb_name)
        fb_interface.FBInterface.__init__(self, fb_name, fb_type, fb_xml, monitor)

        self.fb_obj = fb_obj
        self.kill_event = threading.Event()
        self.execution_end = threading.Event()
        self.ua_variables_update = None
        self.update_variables_fboot = None
        self.fb_type = fb_type

        if fb_type != 'TEST_FB' and fb_name != 'START':
            # Gets the dir path to the py and fbt files
            root_path = utils.get_fb_files_path(fb_type)
            # Gets the file path to the python file
            py_path = os.path.join(root_path, fb_type + '.py')
            message_queue = queue.Queue()
            self.message_queue = message_queue
            self.sniffer_thread = sniffer.Sniffer(fb_type, py_path, message_queue)
            self.sniffer_thread.start()  

    def run(self):
        logging.info('fb {0} started.'.format(self.fb_name))

        while not self.kill_event.is_set():

            if self.fb_type != 'TEST_FB':
                try:
                    self.fb_obj = self.message_queue.get(False)
                    logging.info('Updated {0}'.format(self.fb_type))
                except queue.Empty:
                    pass

            # clears the event when starts the execution
            self.execution_end.clear()

            self.wait_event()

            if self.kill_event.is_set():
                if self.fb_type != 'TEST_FB':
                    self.sniffer_thread.kill()
                break

            inputs = self.read_inputs()

            logging.info('running fb...')

            try:
                outputs = self.fb_obj.schedule(*inputs)

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
                # If the thread blocks inside any fb method
                if self.kill_event.is_set():
                    break

                if outputs is None:
                    logging.error('Outputs are null, please check {0}.py'.format(self.fb_name))
                    # Stops the thread
                    logging.info('stopping the fb work...')
                    break

                self.update_outputs(outputs)

                # updates the opc-ua interface
                if self.ua_variables_update is not None:
                    self.ua_variables_update()
                
                if self.update_variables_fboot is not None:
                    self.update_variables_fboot()


                # sends a signal when ends execution
                self.execution_end.set()

    def stop(self):

        self.stop_thread = True

        self.kill_event.set()
        self.push_event('unblock', 1)

        try:
            self.fb_obj.__del__()
        except AttributeError as exc:
            logging.warning('can not delete the fb object.')
            logging.warning(exc)

        logging.info('fb {0} stopped.'.format(self.fb_name))

        if self.fb_type != 'TEST_FB':
            self.sniffer_thread.kill()