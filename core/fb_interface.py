import threading
from collections import OrderedDict
from xml.etree import ElementTree as ETree
import logging
import time
import datetime


class FBInterface:

    """
    Monitoring - Just calculate the distance between two 2D points
    """
    def dist(self,p1, p2):
        (x1, y1), (x2, y2) = p1, p2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def avg_dist(self,_x,_y):

        ## Specific imports
        global combinations
        from itertools import combinations
        global math
        import math

        ## Calculate mean distance between all base points for neighbourhood-based methods (e.g. DBSCAN)
        points = list(zip(_x, _y))
        distances = [self.dist(p1, p2) for p1, p2 in combinations(points, 2)]
        return sum(distances) / len(distances)

    def write_2_file(self, vals, method_name, pred_val):

        f = open("{0}{1}__{2}.txt".format(self.monitoring_path, self.fb_name, method_name), "a")
        f.write(str(vals).strip('[]'))
        f.write(",{0}\n".format(pred_val))
        f.close()

    """
    Monitoring - Function that executes the thread routine for monitoring
    """
    def thread_monitoring_classify(self, _new_x):

        for neigh, name, algorithm in self.anomaly_algorithms:

            ## For clustering algorithms that do not have the "predict" function
            if neigh:
                ## normalize and stack data
                temp_data = np.vstack((self.scaler.transform(self.anomaly_data),
                                       self.scaler.transform(np.array(_new_x).reshape(1, -1))))
                prediction = algorithm.fit_predict(self.pca.transform(temp_data))[-1] #get last prediction
            ## For supervised algorithms that do have the "predict" function
            else:
                prediction = algorithm.predict(self.pca.transform(self.scaler.transform(np.array(_new_x).reshape(1, -1))))[0]

            self.write_2_file(np.around(self.pca.transform(self.scaler.transform(np.array(_new_x).reshape(1, -1)))).tolist(), name, prediction)

    """
    Monitoring - Function that filters out outliers before training process
    """
    def thread_monitoring_pre_train(self):
        ########################################################
        ## Normalize and apply PCA to the training data
        result = self.pca.fit_transform(self.scaler.fit_transform(self.anomaly_data))

        ## First element of the Tuple is True or False either if it is a neighbourhood-based method or not
        self.anomaly_algorithms[0][2] = EllipticEnvelope(support_fraction=1, contamination=self.contamination)
        self.anomaly_algorithms[1][2] = DBSCAN(eps=self.avg_dist(result[:, 0], result[:, 1]), metric='euclidean', min_samples=2)
        self.anomaly_algorithms[2][2] = OneClassSVM(kernel='rbf', nu=self.contamination, gamma=0.05)

        ########################################################
        ## Predict outliers - use DBSCAN (unsupervised technique) for first fitering of outliers
        ## get predictions for all training data
        DBSCAN_index = 1
        predictions_temp = self.anomaly_algorithms[DBSCAN_index][2].fit_predict(result)

        #########################################################
        ## Filter data - for each element of the training data
        filtered_anomaly = np.array([])
        for temp_i in np.arange(len(self.anomaly_data)):
            ## If sample is not outlier
            if predictions_temp[temp_i] != -1:
                if len(filtered_anomaly) == 0:
                    filtered_anomaly = self.anomaly_data[temp_i]
                else:
                    filtered_anomaly = np.vstack((filtered_anomaly,self.anomaly_data[temp_i]))

        ##########################################################
        ## Update data
        self.anomaly_data = filtered_anomaly

        ## Train algorithms
        self.thread_monitoring_train()

    """
    Monitoring - Function that executes the thread routine for monitoring
    """
    def thread_monitoring_train(self):

        ## Normalize and apply PCA to the training data
        result = self.pca.fit_transform(self.scaler.fit_transform(self.anomaly_data))

        ## for each algorithm in each function block
        for i in np.arange(len(self.anomaly_algorithms)):

            ## If algorithms do have the "predict" function (Clustering algorithms usually don't have)
            if (not self.anomaly_algorithms[i][0]):
                self.anomaly_algorithms[i][2].fit(result)

            ## Update visualization files
            open("{0}{1}__{2}.txt".format(self.monitoring_path, self.fb_name,  self.anomaly_algorithms[i][1]), "w").close()
            for r in result:
                f = open("{0}{1}__{2}.txt".format(self.monitoring_path, self.fb_name, self.anomaly_algorithms[i][1]), "a")
                f.write(str(np.around(r, 2).tolist()).strip('[]'))
                f.write(",1\n")
                f.close()

    """
    Monitoring - Function that executes the thread routine for monitoring
    """
    def thread_monitoring_collect(self):

        ##########################################
        ## Declarations
        counter = 0
        ##########################################

        ## Make initial overwrite of dataset files
        for _, name, _ in self.anomaly_algorithms:
            f = open("{0}{1}__{2}.txt".format(self.monitoring_path,self.fb_name, name), "w")
            f.write("")
            f.close()

        ## create file for input and output event count
        f = open("{0}{1}.txt".format(self.monitoring_path, self.fb_name), "w")
        f.write("")
        f.close()

        ## Initial sleep waiting for all function blocks
        time.sleep(self.init_time_wait)

        ## While not received the first event
        while (not self.first_event):
            time.sleep(1)

            ## A way to terminate a thread
            if self.stop_thread: break

        ##############################################################
        ## Collecting ssamples for training cycle
        while(True):

            ## Exit thread
            if self.stop_thread: break

            # reset all statistics
            self.reset_monitoring()

            #############################################
            # time to collect data
            if self.first_delta:
                time.sleep(self.time_per_sample)
                self.first_delta = False
            else:
                time.sleep(self.time_delta)
            #############################################

            ## Exit thread
            if self.stop_thread: break

            ## Get new sample from Anomaly Detection
            new_sample = self.get_monitoring()

            ## Collecting phase for each function block
            if (not self.classify):
                ## Append to the array
                if len(self.anomaly_data) == 0:
                    self.anomaly_data = self.anomaly_data + new_sample
                else:
                    self.anomaly_data = np.vstack((self.anomaly_data,new_sample))

                    ################################################
                    ## Update file for visualization purposes
                    for _, name, _ in self.anomaly_algorithms:

                        ## just for visuzalization purposes - remove for accelerated processing
                        if len(self.anomaly_data) >= 2:
                            result = self.pca.fit_transform(self.scaler.fit_transform(self.anomaly_data))

                            open("{0}{1}__{2}.txt".format(self.monitoring_path, self.fb_name, name), "w").close()
                            for r in result:
                                f = open("{0}{1}__{2}.txt".format(self.monitoring_path, self.fb_name, name), "a")
                                f.write(str(np.around(r,2).tolist()).strip('[]'))
                                f.write(",1\n")
                                f.close()
                    ################################################

            ## Classification phase for each function block
            else:
                threading.Thread(target=self.thread_monitoring_classify, args=(new_sample,)).start()
                continue

            #############################################
            ## If in collecting phase
            if (counter < self.training_samples):
                counter += 1

            ## Train algorithms
            elif (counter >= self.training_samples and not self.classify):
                #threading.Thread(target=self.thread_monitoring_train).start()
                threading.Thread(target=self.thread_monitoring_pre_train).start()
                self.classify = True

###############################################################################

    def __init__(self, fb_name, fb_type, xml_root, monitor=None):

        self.fb_name = fb_name
        self.fb_type = fb_type
        self.monitor_fb = monitor
        self.stop_thread = False

        self.event_queue = []

        """
        Each events and variables dictionary contains:
        - name (str): event/variable name
        - type (str): INT, REAL, STRING, BOOL
        - watch (boolean): True, False
        """
        self.input_events = OrderedDict()
        self.output_events = OrderedDict()
        self.input_vars = OrderedDict()
        self.output_vars = OrderedDict()

        logging.info('parsing the fb interface (inputs/outputs events/vars)')

        # Parse the xml (iterates over the root)
        for fb in xml_root:
            # Searches for the interfaces list
            if fb.tag == 'InterfaceList':
                # Iterates over the interface list
                # to find the inputs/outputs
                for interface in fb:
                    # Input events
                    if interface.tag == 'EventInputs':
                        # Iterates over the input events
                        for event in interface:
                            try:
                                event_name = event.attrib['Name']
                                event_type = event.attrib['Type']
                            except KeyError:
                                logging.error('Could not find mandatory attributes "Name" and "Type"')
                                logging.error('Please check {0}.fbt for mistakes'.format(fb_name))
                            else:                           
                                self.input_events[event_name] = (event_type, None, False)

                    # Output Events
                    elif interface.tag == 'EventOutputs':
                        # Iterates over the output events
                        for event in interface:
                            try:
                                event_name = event.attrib['Name']
                                event_type = event.attrib['Type']
                            except KeyError:
                                logging.error('Could not find mandatory attributes "Name" and "Type"')
                                logging.error('Please check {0}.fbt for mistakes'.format(fb_name))
                            else:
                                self.output_events[event_name] = (event_type, None, False)
                            
                    # Input vars
                    elif interface.tag == 'InputVars':
                        # Iterates over the input vars
                        for var in interface:
                            try:
                                var_name = var.attrib['Name']
                                var_type = var.attrib['Type']
                            except KeyError:
                                logging.error('Could not find mandatory attributes "Name" and "Type"')
                                logging.error('Please check {0}.fbt for mistakes'.format(fb_name))
                            else:
                                self.input_vars[var_name] = (var_type, None, False)

                    # Output vars
                    elif interface.tag == 'OutputVars':
                        # Iterates over the output vars
                        for var in interface:
                            try:
                                var_name = var.attrib['Name']
                                var_type = var.attrib['Type']
                            except KeyError:
                                logging.error('Could not find mandatory attributes "Name" and "Type"')
                                logging.error('Please check {0}.fbt for mistakes'.format(fb_name))
                            else:
                                self.output_vars[var_name] = (var_type, None, False)

                    # Doesn't expected interface
                    else:
                        logging.error("doesn't expected interface (check interface name in .fbt file)")

        logging.info('parsing successful with:')
        logging.info('input events: {0}'.format(self.input_events))
        logging.info('output events: {0}'.format(self.output_events))
        logging.info('input vars: {0}'.format(self.input_vars))
        logging.info('output vars: {0}'.format(self.output_vars))

        self.output_connections = dict()

        self.new_event = threading.Event()

        self.lock = threading.Lock()

        ###############################################################
        ## If we want to monitor the FB
        if self.monitor_fb is not None:
            #############################################
            ## All key imports
            global svm
            from sklearn import svm
            global EllipticEnvelope
            from sklearn.covariance import EllipticEnvelope
            global IsolationForest
            from sklearn.ensemble import IsolationForest
            global LocalOutlierFactor
            from sklearn.neighbors import LocalOutlierFactor
            global PCA
            from sklearn.decomposition import PCA
            global StandardScaler
            from sklearn.preprocessing import StandardScaler
            global DBSCAN
            from sklearn.cluster import DBSCAN
            global OneClassSVM
            from sklearn.svm import OneClassSVM
            global np
            import numpy as np
            global pd
            import pandas as pd
            global os
            import os
            global sys
            import sys

            """
            Monitoring variables for Behavioral Anomaly Detection
            """
            self.time_in = pd.DataFrame(columns=['time'])
            self.time_out = pd.DataFrame(columns=['time'])

            #############################################
            ## Monitoring - Create thread
            self.training_samples, self.time_per_sample = self.monitor_fb

            ## Time lag like in predicive maintenance approaches
            self.training_samples = (self.training_samples*4) - 3
            self.time_delta = int(self.time_per_sample/4)
            self.first_delta = True

            self.init_time_wait = 5
            self.moni_thread = threading.Thread(target=self.thread_monitoring_collect)
            self.classify = False
            self.contamination = 1/self.training_samples
            self.anomaly_data = []
            self.first_event = False
            self.monitoring_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'monitoring','')

            ## Pre-processing Methods
            self.pca = PCA(n_components=2)
            self.scaler = StandardScaler()
            ## First element of the Tuple is True or False either if it is a neighbourhood-based method or not
            self.anomaly_algorithms = [
                [False, "Empirical Covariance", None],
                [True, "DBSCAN", None],
                [False, "One Class SVM", None]]

            #########################
            ## Monitoring - Start thread
            self.moni_thread.start()
            #########################

            #############################################

    def set_attr(self, name, new_value=None, set_watch=None):
        # Locks the dictionary usage
        self.lock.acquire()
        try:
            # INPUT VAR
            if name in self.input_vars:
                v_type, value, is_watch = self.input_vars[name]
                # Sets the watch
                if set_watch is not None:
                    self.input_vars[name] = (v_type, value, set_watch)
                # Sets the var value
                elif new_value is not None:
                    self.input_vars[name] = (v_type, new_value, is_watch)

            # INPUT EVENT
            elif name in self.input_events:
                event_type, value, is_watch = self.input_events[name]
                # Sets the watch
                if set_watch is not None:
                    self.input_events[name] = (event_type, value, set_watch)
                # Sets the event value
                elif new_value is not None:
                    self.input_events[name] = (event_type, new_value, is_watch)

            # OUTPUT VAR
            elif name in self.output_vars:
                var_type, value, is_watch = self.output_vars[name]
                # Sets the watch
                if set_watch is not None:
                    self.output_vars[name] = (var_type, value, set_watch)
                # Sets the var value
                elif new_value is not None:
                    self.output_vars[name] = (var_type, new_value, is_watch)

            # OUTPUT EVENT
            elif name in self.output_events:
                event_type, value, is_watch = self.output_events[name]
                # Sets the watch
                if set_watch is not None:
                    self.output_events[name] = (event_type, value, set_watch)
                # Sets the event value
                elif new_value is not None:
                    self.output_events[name] = (event_type, new_value, is_watch)

        finally:
            # Unlocks the dictionary usage
            self.lock.release()

    def read_attr(self, name):
        v_type = None
        value = None
        is_watch = None

        # Locks the dictionary usage
        self.lock.acquire()
        try:
            # INPUT VAR
            if name in self.input_vars:
                v_type, value, is_watch = self.input_vars[name]

            # INPUT EVENT
            elif name in self.input_events:
                v_type, value, is_watch = self.input_events[name]

            # OUTPUT VAR
            elif name in self.output_vars:
                v_type, value, is_watch = self.output_vars[name]

            # OUTPUT EVENT
            elif name in self.output_events:
                v_type, value, is_watch = self.output_events[name]

        except KeyError as error:
            logging.error('can not find that fb attribute')
            logging.error(error)

        finally:
            # Unlocks the dictionary usage
            self.lock.release()

        return v_type, value, is_watch

    def add_connection(self, value_name, connection):
        # If already exists a connection
        if value_name in self.output_connections:
            conns = self.output_connections[value_name]
            conns.append(connection)

        # If don't exists any connection with that value
        else:
            conns = [connection]
            self.output_connections[value_name] = conns

    def push_event(self, event_name, event_value):
        if event_value is not None:
            self.event_queue.append((event_name, event_value))
            # Updates the event value
            self.set_attr(event_name, new_value=event_value)
            # Sets the new event
            self.new_event.set()

    def pop_event(self):
        if len(self.event_queue) > 0:

            ## pop event
            event_name, event_value = self.event_queue.pop()

            if self.monitor_fb:
                ############################################
                ## Event In - read from my own FB queue
                self.time_in = self.time_in.append({'time': datetime.datetime.now()}, ignore_index=True)
                ############################################

                if not self.first_event and event_name != 'INIT':
                    self.first_event = True

            return event_name, event_value

    def wait_event(self):
        while len(self.event_queue) <= 0:
            self.new_event.wait()
            # Clears new_event to wait for new events
            self.new_event.clear()
        # Clears new_event to wait for new events
        self.new_event.clear()

    def read_inputs(self):
        logging.info('reading fb inputs...')

        # First convert the vars dictionary to a list
        events_list = []
        event_name, event_value = self.pop_event()
        self.set_attr(event_name, new_value=event_value)
        events_list.append(event_name)
        events_list.append(event_value)

        # Second converts the event dictionary to a list
        vars_list = []
        logging.info('input vars: {0}'.format(self.input_vars))
        # Get all the vars
        for index, var_name in enumerate(self.input_vars):
            v_type, value, is_watch = self.read_attr(var_name)
            vars_list.append(value)

        # Finally concatenate the 2 lists
        return events_list + vars_list

    def update_outputs(self, outputs):
        logging.info('updating the outputs...')

        # Converts the second part of the list to variables
        for index, var_name in enumerate(self.output_vars):
            # Second part of the list delimited by the events dictionary len
            new_value = outputs[index + len(self.output_events)]

            # Updates the var value
            self.set_attr(var_name, new_value=new_value)

            # Verifies if exist any connection
            if var_name in self.output_connections:
                # Updates the connection
                for connection in self.output_connections[var_name]:
                    connection.update_var(new_value)

        # Converts the first part of the list to events
        for index, event_name in enumerate(self.output_events):
            value = outputs[index]
            self.set_attr(event_name, new_value=value)

            # Verifies if exist any connection
            if event_name in self.output_connections:

                if self.monitor_fb and value is not None:
                    ############################################
                    ## Event Out - send events to subsequent FB
                    self.time_out = self.time_out.append({'time': datetime.datetime.now()}, ignore_index=True)
                    ############################################

                # Sends the event ot the new fb
                for connection in self.output_connections[event_name]:
                    connection.send_event(value)

    def read_watches(self, start_time):
        # Creates the xml root element
        fb_root = ETree.Element('FB', {'name': self.fb_name})

        # Mixes the vars in 1 dictionary
        var_mix = {**self.input_vars, **self.output_vars}
        # Iterates over the mix dictionary
        for index, var_name in enumerate(var_mix):
            v_type, value, is_watch = self.read_attr(var_name)
            if is_watch and (value is not None):
                port = ETree.Element('Port', {'name': var_name})
                ETree.SubElement(port, 'Data', {'value': str(value)[0:100],
                                                'forced': 'false'})
                fb_root.append(port)

        # Mixes the vars in 1 dictionary
        event_mix = {**self.input_events, **self.output_events}
        # Iterates over the mix dictionary
        for index, event_name in enumerate(event_mix):
            v_type, value, is_watch = self.read_attr(event_name)
            if is_watch and (value is not None):
                port = ETree.Element('Port', {'name': event_name})
                ETree.SubElement(port, 'Data', {'value': str(value)[0:100],
                                                'time': str(int((time.time() * 1000) - start_time))})
                fb_root.append(port)

        # Gets the number of watches
        watches_len = len(fb_root.findall('Port'))

        return fb_root, watches_len

    ## Reset the monitoring statistics
    def reset_monitoring(self):
        """
        Monitoring variables for Behavioral Anomaly Detection
        """
        full_delta = datetime.datetime.now() - datetime.timedelta(seconds=self.time_per_sample + 5)

        self.time_in = self.time_in[self.time_in.time > full_delta]
        self.time_out = self.time_out[self.time_out.time > full_delta]

    ## Get the monitoring statistics for further processing
    def get_monitoring(self):

        #print(self.fb_name , self.time_in)
        #print(self.fb_name , self.time_out)


        time_now = datetime.datetime.now()
        full_delta = time_now - datetime.timedelta(seconds=self.time_per_sample)
        half_delta = time_now - datetime.timedelta(seconds=int(self.time_per_sample/2))
        quarter_delta = time_now - datetime.timedelta(seconds=int(self.time_per_sample/4))

        df_in_full = self.time_in[self.time_in.time > full_delta]
        df_in_half = self.time_in[self.time_in.time > half_delta]
        df_in_quarter= self.time_in[self.time_in.time > quarter_delta]

        df_out_full = self.time_out[self.time_out.time > full_delta]
        df_out_half = self.time_out[self.time_out.time > half_delta]
        df_out_quarter = self.time_out[self.time_out.time > quarter_delta]

        ## calculating differences
        diff_df_in_full = (df_in_full['time'] - df_in_full['time'].shift(1)) / np.timedelta64(1, 's')
        diff_df_in_full = diff_df_in_full[1:]
        diff_df_in_half = (df_in_half['time'] - df_in_half['time'].shift(1)) / np.timedelta64(1, 's')
        diff_df_in_half = diff_df_in_half[1:]
        diff_df_in_quarter = (df_in_quarter['time'] - df_in_quarter['time'].shift(1)) / np.timedelta64(1, 's')
        diff_df_in_quarter = diff_df_in_quarter[1:]

        diff_df_out_full = (df_out_full['time'] - df_out_full['time'].shift(1)) / np.timedelta64(1, 's')
        diff_df_out_full = diff_df_out_full[1:]
        diff_df_out_half = (df_out_half['time'] - df_out_half['time'].shift(1)) / np.timedelta64(1, 's')
        diff_df_out_half = diff_df_out_half[1:]
        diff_df_out_quarter = (df_out_quarter['time'] - df_out_quarter['time'].shift(1)) / np.timedelta64(1, 's')
        diff_df_out_quarter = diff_df_out_quarter[1:]

        #######################################
        ## write file with event_queue size

        f = open("{0}{1}.txt".format(self.monitoring_path, self.fb_name), "a")
        f.write("{0},{1}\n".format(df_in_full['time'].count(),df_out_full['time'].count()))
        f.close()

        #######################################

        return [diff_df_in_quarter.count(),
                0 if diff_df_in_quarter.count() == 0 else round(diff_df_in_quarter.mean(),4),
                0 if diff_df_in_quarter.count() <= 1 else round(diff_df_in_quarter.std(),4),
                diff_df_in_half.count(),
                0 if diff_df_in_half.count() == 0 else round(diff_df_in_half.mean(),4),
                0 if diff_df_in_half.count() <= 1 else round(diff_df_in_half.std(),4),
                diff_df_in_full.count(),
                0 if diff_df_in_full.count() == 0 else round(diff_df_in_full.mean(),4),
                0 if diff_df_in_full.count() <= 1 else round(diff_df_in_full.std(),4),
                diff_df_out_quarter.count(),
                0 if diff_df_out_quarter.count() == 0 else round(diff_df_out_quarter.mean(), 4),
                0 if diff_df_out_quarter.count() <= 1 else round(diff_df_out_quarter.std(), 4),
                diff_df_out_half.count(),
                0 if diff_df_out_half.count() == 0 else round(diff_df_out_half.mean(), 4),
                0 if diff_df_out_half.count() <= 1 else round(diff_df_out_half.std(), 4),
                diff_df_out_full.count(),
                0 if diff_df_out_full.count() == 0 else round(diff_df_out_full.mean(), 4),
                0 if diff_df_out_full.count() <= 1 else round(diff_df_out_full.std(), 4)]


class Connection:

    def __init__(self, destination_fb, value_name):
        self.destination_fb = destination_fb
        self.value_name = value_name

    def update_var(self, value):
        self.destination_fb.set_attr(self.value_name, new_value=value)

    def send_event(self, value):
        self.destination_fb.push_event(self.value_name, value)
