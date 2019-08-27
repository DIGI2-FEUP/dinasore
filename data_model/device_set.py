from data_model import utils
from data_model import ua_base
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
                fb_name = dev_xml.attrib['id']
                fb_type = dev_xml.attrib['dId']
                # creates the device
                dev = ua_base.UaBaseLayer2(self.__ua_peer, fb_name, fb_type, 'DeviceSet', 'Device')
                dev.parse_loop_type_xml(dev_xml)
                # use the fb_name as key
                self.devices_dict[dev.fb_name] = dev

    def from_fb(self, fb, fb_xml):
        # creates the device
        dev = ua_base.UaBaseLayer2(self.__ua_peer, fb.fb_name, fb.fb_type, 'DeviceSet', 'Device')
        # links the fb to the device
        dev.parse_loop_type_fb(fb, fb_xml)
        # adds the device to the dictionary
        self.devices_dict[dev.fb_name] = dev

    def save_xml(self, xml_set):
        # iterates over the devices dictionary and creates each device
        for key, device_item in self.devices_dict.items():
            # creates the device element
            device_xml = ETree.SubElement(xml_set, 'device')
            # creates the content off that device
            device_item.save_all_xml(device_xml)
