from data_model_fboot import utils
import logging
import uuid


class UaObject:

    class InvalidFbtState(Exception):
        pass

    def __init__(self, ua_server, ua_folder, fb_name, xml_root):
        self.ua_server = ua_server
        self.ua_folder = ua_folder
        self.fb_name = fb_name
        self.xml_root = xml_root
        self.fb_type = xml_root.get('Name')
        self.opc_ua_type = xml_root.get('OpcUa')
        self.folders = dict()
        self.ua_vars = dict()
        # creates the fb inside the configuration
        self.ua_server.config.create_virtualized_fb(self.fb_name, self.fb_type, self.update_variables)
        # creates required connections
        self.set_up_connections()
        # create object
        self.obj_idx = '{0}:{1}'.format(ua_folder.get('idx'), self.fb_name)
        self.obj_path_list, self.obj_path = utils.default_object(ua_server, 
                                                                self.obj_idx, 
                                                                ua_folder.get('path'), 
                                                                ua_folder.get('path_list'), 
                                                                self.fb_name)
        # create variables and events folders
        var_folder_idx, var_folder_path, var_folder_list =  utils.default_folder(ua_server, 
                                                                                self.obj_idx, 
                                                                                self.obj_path, 
                                                                                self.obj_path_list, 
                                                                                'Variables')
        var_folder = {
            'idx': var_folder_idx,
            'path': var_folder_path,
            'path_list': var_folder_list
        }
        self.folders['VarFolder'] = var_folder
        event_folder_idx, event_folder_path, event_folder_list =  utils.default_folder(ua_server, 
                                                                                    self.obj_idx, 
                                                                                    self.obj_path, 
                                                                                    self.obj_path_list, 
                                                                                    'Events')
        event_folder = {
            'idx': event_folder_idx,
            'path': event_folder_path,
            'path_list': event_folder_list
        }
        self.folders['EventFolder'] = event_folder
        # populate vars and events folders
        try:
            self.populate_vars_folder()
            self.populate_events_folder()
        except self.InvalidFbtState:
            logging.error('Invalid function block definition, check {0}.fbt for mistakes'.format(self.fb_name))

    def populate_vars_folder(self):
        for child in self.xml_root: # InterfaceList
            if child.tag != 'InterfaceList':
                raise self.InvalidFbtState
            for element in child: # Event and Vars Inputs/Outputs
                if element.tag == 'InputVars' or element.tag == 'OutputVars':
                    for var_declaration in element: # Var Declarations
                        if var_declaration.tag != 'VarDeclaration':
                            raise self.InvalidFbtState
                        if 'OpcUa' in var_declaration.attrib:
                            try:
                                var_idx = '{0}:{1}'.format(self.folders['VarFolder'].get('idx'), var_declaration.get('Name'))
                                ua_var = self.ua_server.create_typed_variable(self.folders['VarFolder'].get('path'),
                                                                    var_idx,
                                                                    var_declaration.get('Name'), 
                                                                    utils.UA_TYPES[var_declaration.get('Type')], 
                                                                    0)
                                self.ua_vars[var_declaration.get('Name')] = ua_var
                            except KeyError:
                                raise self.InvalidFbtState

    def populate_events_folder(self):
        for child in self.xml_root: # InterfaceList
            if child.tag != 'InterfaceList':
                raise self.InvalidFbtState
            for element in child: # Event and Vars Inputs/Outputs
                if element.tag == 'EventInputs' or element.tag == 'EventOutputs':
                    for event in element: # Events
                        if event.tag != 'Event':
                            raise self.InvalidFbtState
                        try:
                            var_idx = '{0}:{1}'.format(self.folders['EventFolder'].get('idx'), event.get('Name'))
                            ua_var = self.ua_server.create_typed_variable(self.folders['EventFolder'].get('path'),
                                                                var_idx,
                                                                event.get('Name'), 
                                                                utils.UA_TYPES['String'], 
                                                                0)
                            self.ua_vars[event.get('Name')] = ua_var
                        except KeyError as ke:
                            print('Accessed non existent attrib {0}'.format(ke.args))
                            raise self.InvalidFbtState

    def set_up_connections(self):
        if self.opc_ua_type == 'DEVICE.SENSOR':
            self.ua_server.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))
            # creates the fb that runs the device in loop
            sleep_fb_name = str(uuid.uuid4())
            self.ua_server.config.create_fb(sleep_fb_name, 'SLEEP')
            self.ua_server.config.create_connection('{0}.{1}'.format(self.fb_name, 'INIT_O'),
                                                '{0}.{1}'.format(sleep_fb_name, 'SLEEP'))
            self.ua_server.config.create_connection('{0}.{1}'.format(sleep_fb_name, 'SLEEP_O'),
                                                '{0}.{1}'.format(self.fb_name, 'READ'))
            self.ua_server.config.create_connection('{0}.{1}'.format(self.fb_name, 'READ_O'),
                                                '{0}.{1}'.format(sleep_fb_name, 'SLEEP'))
        else:
            self.ua_server.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                              '{0}.{1}'.format(self.fb_name, 'INIT'))

    def update_variables(self):
        # gets the function block
        fb = self.ua_server.config.get_fb(self.fb_name)
        # iterates over the variables dict
        for var_name, var_ua in self.ua_vars.items():
            # reads the variable value
            v_type, value, _ = fb.read_attr(var_name)

            try:
                # writes the value inside the opc-ua variable
                var_ua.set_value(value)

            except Exception as error:
                # reports the error
                logging.warning('Error writing the value in the opc-ua server.')
                logging.warning(error)
                if v_type == 'STRING':
                    # writes the value as a string
                    var_ua.set_value(str(value))
                    # writes the solution
                    logging.warning('Error solved writing the variable as string.')
                        
    
    
