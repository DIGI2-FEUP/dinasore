from threading import Thread
from threading import Event
from data_model import utils
import psutil


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
        var_names = ('CPU_PERCENT', 'CPU_FREQ_CURRENT', 'CPU_FREQ_MIN', 'CPU_FREQ_MAX',
                     'MEM_TOTAL', 'MEM_AVAILABLE', 'MEM_PERCENTAGE', 'MEM_USED', 'MEM_CACHED', 'MEM_SHARED')
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

    def run(self):
        # monitor the hardware until kill event
        while not self.kill_event.is_set():
            # reads the values
            measures = self.measure_hardware()
            tuple_vars = zip(self.ua_vars_dict.values(), measures)
            # iterates over the tuples and writes ua value
            for ua_var, value in tuple_vars:
                ua_var.set_value(value)
            # waits n seconds
            self.kill_event.wait(1)

    @staticmethod
    def measure_hardware():
        # cpu variables
        cpu_percent = [psutil.cpu_percent()]
        cpu_freq_tuple = list(psutil.cpu_freq())
        # memory variables
        mem_tuple = list(psutil.virtual_memory())
        # return a tuple with all
        return cpu_percent + cpu_freq_tuple + mem_tuple[0:4] + mem_tuple[8:10]

    def stop(self):
        self.kill_event.set()
