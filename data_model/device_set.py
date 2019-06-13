from data_model import utils
from data_model import device


class DeviceSet:

    def __init__(self, ua_peer):
        self.__devices = dict()
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
                dev = device.Device(self.__ua_peer)
                dev.from_xml(dev_xml)

                # use the fb_name as key
                self.__devices[dev.subs_id] = dev

    def from_fb(self, fb, fb_xml):

        # creates the device
        dev = device.Device(self.__ua_peer)
        # links the fb to the device
        dev.from_fb(fb, fb_xml)

        # adds the device to the dictionary
        self.__devices[dev.subs_id] = dev

    def search_device(self, dev_id):
        if dev_id in self.__devices:
            return self.__devices[dev_id]
        else:
            return None
