from threading import Thread
from threading import Event
from data_model_fboot import utils
import psutil
import os
import sys


class MonitorSystem(Thread):
    # creates the event kill thread event
    kill_event = Event()

    def __init__(self, ua_peer):
        Thread.__init__(self, name='monitoring_thread')
        self.kill_event.clear()
        # creates the opc-ua folder
        folder_idx, folder_path, folder_list = utils.default_folder(ua_peer, ua_peer.base_idx,
                                                                    ua_peer.ROOT_PATH, ua_peer.ROOT_LIST,
                                                                    'HardwareMonitoring')
        # variables names
        var_names = ('CPU_PERCENT', 'CPU_FREQ_CURRENT', 'MEM_AVAILABLE', 
                    'MEM_PERCENTAGE', 'MEM_USED', 'MEM_CACHED', 'MEM_SHARED')
        # zips both names and values in on dict
        tuple_vars = zip(var_names, self.measure_hardware())

        # ua variables
        ua_vars = []
        for var_name, var_value in tuple_vars:
            var_idx = '{0}:{1}'.format(folder_idx, var_name)
            browse_name = '2:{0}'.format(var_name)
            ua_var = ua_peer.create_variable(folder_path, var_idx, browse_name, var_value)
            ua_vars.append(ua_var)

        # joins the ua variables with the names
        self.ua_vars_dict = dict(zip(var_names, ua_vars))

        # open logs file
        self.logs_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'error_list.log')

        # create ua variable for log
        self.ua_log = ua_peer.create_variable(folder_path, 
                                            '{0}:ERROR_LOG'.format(folder_idx),
                                            '2:ERROR_LOG',
                                            '')

    def run(self):
        # monitor the hardware until kill event
        while not self.kill_event.is_set():
            # reads the values
            measures = self.measure_hardware()
            tuple_vars = zip(self.ua_vars_dict.values(), measures)
            # iterates over the tuples and writes ua value
            for ua_var, value in tuple_vars:
                ua_var.set_value(value)
            # updates log variable
            with open(self.logs_path, 'r') as logs_file:
                self.ua_log.set_value(logs_file.read())
            # waits n seconds
            self.kill_event.wait(1)

    @staticmethod
    def measure_hardware():
        # cpu variables
        cpu_percent = [psutil.cpu_percent()]
        cpu_freq = [psutil.cpu_freq()[0]]
        # memory variables
        mem_tuple = list(psutil.virtual_memory())
        # return a tuple with all
        return cpu_percent + cpu_freq + mem_tuple[1:4] + mem_tuple[8:10]

    def stop(self):
        self.kill_event.set()
