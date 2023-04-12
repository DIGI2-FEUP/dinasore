import multiprocessing
import logging
from core import fb_interface


class FB(multiprocessing.Process, fb_interface.FBInterface):

    def __init__(self, fb_name, fb_type, fb_obj, fb_xml):
        multiprocessing.Process.__init__(self, name=fb_name)
        fb_interface.FBInterface.__init__(self, fb_name, fb_type, fb_xml)

        self.fb_obj = fb_obj
        self.execution_end = multiprocessing.Event()

    def run(self):
        logging.info('fb {0} started.'.format(self.fb_name))

        # Executes the FB in cycle
        while True:
            # clears the event when starts the execution
            self.execution_end.clear()
            self.wait_event()
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
                self.update_outputs(outputs)
                # sends a signal when ends execution
                self.execution_end.set()
