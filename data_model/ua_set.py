from data_model import utils
from data_model import ua_object
import xml.etree.ElementTree as ETree


class UaSet(utils.UaInterface):

    def __init__(self, ua_peer, set_xml_name, item_xml_name, loop_type=False):
        self.items_dict = dict()
        # receives the peer methods to add the opc-ua objects
        self.ua_peer = ua_peer
        # set settings
        # 'DeviceSet', 'ServiceInstanceSet'
        self.set_xml_name = set_xml_name
        # 'device', 'serviceinstance'
        self.item_xml_name = item_xml_name
        # 'Device', 'Instance'
        self.loop_type = loop_type

        # creates the opc-ua folder
        utils.default_folder(self.ua_peer, self.ua_peer.base_idx,
                             self.ua_peer.ROOT_PATH, self.ua_peer.ROOT_LIST, self.set_xml_name)

    def from_xml(self, xml_set):
        # iterates over all devices
        for item_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = item_xml.tag[1:].partition("}")
            if tag == self.item_xml_name:
                # parses the first attributes
                fb_name = item_xml.attrib['id']
                fb_type = item_xml.attrib['dId']
                source_type = item_xml.attrib['type']
                # creates the device
                new_item = ua_object.UaObject(self.ua_peer, fb_name, fb_type,
                                              source_type=source_type,
                                              browse_name=fb_name,
                                              root_folder=self.set_xml_name)
                # checks if is a loop type
                if self.loop_type:
                    new_item.parse_loop_type_xml(item_xml)
                # otherwise is a service type
                else:
                    new_item.parse_service_type_xml(item_xml)

                # use the fb_name as key
                self.items_dict[new_item.fb_name] = new_item

    def parse_all_subscriptions(self, xml_set):
        for item_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = item_xml.tag[1:].partition("}")
            if tag == self.item_xml_name:
                # parses the first attributes
                fb_name = item_xml.attrib['id']
                # parse the subscriptions
                self.items_dict[fb_name].parse_subscriptions(item_xml)

    def from_fb(self, fb, fb_xml):
        # gets the source type
        item_type = fb_xml.attrib['OpcUa'].split('.')
        # creates the device
        new_item = ua_object.UaObject(self.ua_peer, fb.fb_name, fb.fb_type,
                                      source_type=item_type[1] if len(item_type) > 1 else item_type[0],
                                      browse_name=fb.fb_name,
                                      root_folder=self.set_xml_name)
        # checks if is a loop type
        if self.loop_type:
            new_item.parse_loop_type_fb(fb, fb_xml)
        # otherwise is a service type
        else:
            new_item.parse_service_type_fb(fb, fb_xml)
        # adds the device to the dictionary
        self.items_dict[new_item.fb_name] = new_item

    def save_xml(self, xml_set):
        # iterates over the devices dictionary and creates each device
        for key, item in self.items_dict.items():
            # creates the device element
            xml2save = ETree.SubElement(xml_set, self.item_xml_name)
            # creates the content off that device
            item.save_all_xml(xml2save)
