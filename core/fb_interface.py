import threading
from collections import OrderedDict
from xml.etree import ElementTree as ETree
import logging
import time


class FBInterface:

    def __init__(self, fb_name, fb_type, xml_root):

        self.fb_name = fb_name
        self.fb_type = fb_type
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

        # checks if is a loop fb
        self.loop_fb = False
        if 'OpcUa' in xml_root.attrib:
            if xml_root.attrib['OpcUa'] == 'DEVICE.SENSOR':
                self.loop_fb = True
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
                            event_name = event.attrib['Name']
                            event_type = event.attrib['Type']
                            self.input_events[event_name] = (event_type, None, False)

                    # Output Events
                    elif interface.tag == 'EventOutputs':
                        # Iterates over the output events
                        for event in interface:
                            event_name = event.attrib['Name']
                            event_type = event.attrib['Type']
                            self.output_events[event_name] = (event_type, None, False)

                    # Input vars
                    elif interface.tag == 'InputVars':
                        # Iterates over the input vars
                        for var in interface:
                            var_name = var.attrib['Name']
                            var_type = var.attrib['Type']
                            self.input_vars[var_name] = (var_type, None, False)

                    # Output vars
                    elif interface.tag == 'OutputVars':
                        # Iterates over the output vars
                        for var in interface:
                            var_name = var.attrib['Name']
                            var_type = var.attrib['Type']
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
            # pop event
            event_name, event_value = self.event_queue.pop()
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
                ETree.SubElement(port, 'Data', {'value': str(value),
                                                'forced': 'false'})
                fb_root.append(port)

        # Mixes the vars in 1 dictionary
        event_mix = {**self.input_events, **self.output_events}
        # Iterates over the mix dictionary
        for index, event_name in enumerate(event_mix):
            v_type, value, is_watch = self.read_attr(event_name)
            if is_watch and (value is not None):
                port = ETree.Element('Port', {'name': event_name})
                ETree.SubElement(port, 'Data', {'time': str(int((time.time() * 1000) - start_time)),
                                                'value': str(value)})
                fb_root.append(port)

        # Gets the number of watches
        watches_len = len(fb_root.findall('Port'))

        return fb_root, watches_len


class Connection:

    def __init__(self, destination_fb, value_name):
        self.destination_fb = destination_fb
        self.value_name = value_name

    def update_var(self, value):
        self.destination_fb.set_attr(self.value_name, new_value=value)

    def send_event(self, value):
        self.destination_fb.push_event(self.value_name, value)
