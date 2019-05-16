from core import fb_resources


class DeviceSet:

    def __init__(self):
        self.devices = dict()

    def parse_xml(self, xml_set, config):

        for dev_xml in xml_set:
            if dev_xml.tag == 'device':
                dev = Device(dev_xml.attrib['id'],
                             dev_xml.attrib['type'])
                dev.parse_xml(dev_xml, config)

                self.devices[dev_xml.attrib['id']] = dev

    def add_device(self, fb_type, fb):
        # get the xml fb definition xml file
        fb = fb_resources.FBResources(fb_type)

        # gets the device id and type
        dev_id, dev_type = fb.get_description()
        # creates the device
        dev = Device(dev_id, dev_type)
        # links the fb to the device
        dev.link_fb(fb)

        # adds the device to the dictionary
        self.devices[dev_id] = dev


class Device:

    def __init__(self, dev_id, dev_type):
        self.dev_id = dev_id
        self.dev_type = dev_type

        self.ua_methods = dict()
        self.ua_variables = dict()

        self.diac_methods = dict()
        self.diac_variables = dict()

    def parse_xml(self, root_xml, config):
        fb_type = fb_resources.GeneralResources().search_description(self.dev_id)

        # creates the respective fb
        index = 1
        fb_name = fb_type
        while True:
            # search if exists any fb with this name
            if fb_name not in config.fb_dictionary:
                config.create_fb(fb_name, fb_type)
                break
            # creates a new name for this fb
            fb_name = "{0}{1}".format(fb_type, index)
            index += 1

        # gets the created fb
        fb = config.get_fb(fb_name)

        for item in root_xml:
            # link opc-ua variables in fb input variable
            if item.tag == 'variables':
                for variable in item:
                    var_name = variable.attrib['name']
                    # checks if exists any variable with these name
                    if var_name in fb.input_vars:
                        # creates the opc-ua variable
                        pass

            # link opc-ua methods in fb methods
            elif item.tag == 'methods':
                for method in item:
                    pass

            elif item.tag == 'subscriptions':
                for subs in item:
                    pass

    def link_fb(self, fb):
        pass

    def virtualize_variable(self):
        pass

