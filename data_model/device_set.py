from data_model import utils
from data_model import device
import xml.etree.ElementTree as ETree


class DeviceSet(utils.UaInterface):

    def __init__(self, ua_peer):
        self.devices_dict = dict()
        # receives the peer methods to add the opc-ua objects
        self.__ua_peer = ua_peer

        # creates the opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'DeviceSet')

    def from_xml(self, xml_set):
        for dev_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = dev_xml.tag[1:].partition("}")

            if tag == 'device':
                # parses the first attributes
                subs_id = dev_xml.attrib['id']
                fb_name, fb_type, state = self.__parse_xml_header(dev_xml)
                # creates the device
                dev = device.Device(self.__ua_peer, subs_id, fb_name, fb_type, state, 'DeviceSet')
                dev.from_xml(dev_xml)
                # use the fb_name as key
                self.devices_dict[dev.subs_id] = dev

    def from_fb(self, fb, fb_xml):
        # creates the device
        dev = device.Device(self.__ua_peer, fb.fb_name, fb.fb_name, fb.fb_type, 'RUNNING', 'DeviceSet')
        # links the fb to the device
        dev.from_fb(fb, fb_xml)
        # adds the device to the dictionary
        self.devices_dict[dev.subs_id] = dev

    def save_xml(self, xml_set):
        # iterates over the devices dictionary and creates each device
        for key, device_item in self.devices_dict.items():
            # creates the device element
            device_xml = ETree.SubElement(xml_set, 'device')
            # creates the content off that device
            device_item.save_xml(device_xml)

    @staticmethod
    def __parse_xml_header(header_xml):
        fb_name, fb_type, state = None, None, None
        # creates the device object
        for variables in header_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = variables.tag[1:].partition("}")

            if tag == 'variables':
                for var in variables:
                    if var.attrib['name'] == 'Description':
                        # creates the device properties
                        for element in var[0]:
                            # creates the opc-ua object
                            if element.attrib['id'] == 'Name':
                                fb_name = element.text

                            # creates the fb
                            elif element.attrib['id'] == 'SourceType':
                                fb_type = element.text

                            # creates the state
                            elif element.attrib['id'] == 'SourceState':
                                state = element.text

        return fb_name, fb_type, state
