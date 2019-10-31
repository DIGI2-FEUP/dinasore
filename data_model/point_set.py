from data_model import ua_object
from data_model import ua_set
import xml.etree.ElementTree as ETree


class PointSet(ua_set.UaSet):

    def __init__(self, ua_peer):
        ua_set.UaSet.__init__(self, ua_peer, set_xml_name='PointSet', item_xml_name='', loop_type=True)

    def from_xml(self, item_xml):
        for point_xml in item_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = point_xml.tag[1:].partition("}")
            if tag == 'startpointdescription':
                # gets the attributes
                fb_name = point_xml.attrib['id']
                fb_type = point_xml.attrib['dId']
                # creates the start point
                start_point = ua_object.UaObject(self.ua_peer, fb_name, fb_type,
                                                 source_type='StartPoint',
                                                 browse_name=fb_name,
                                                 root_folder='PointSet')
                # parses the xml
                start_point.parse_loop_type_xml(point_xml)
                # saves the endpoint
                self.items_dict[fb_name] = start_point

            elif tag == 'endpointdescription':
                # gets the attributes
                fb_name = point_xml.attrib['id']
                fb_type = point_xml.attrib['dId']
                # creates the endpoint
                end_point = ua_object.UaObject(self.ua_peer, fb_name, fb_type,
                                               source_type='EndPoint',
                                               browse_name=fb_name,
                                               root_folder='PointSet')
                # parses the xml
                end_point.parse_service_type_xml(point_xml)
                # saves the endpoint
                self.items_dict[fb_name] = end_point

    def parse_all_subscriptions(self, xml_set):
        for point_xml in xml_set:
            # splits the tag in these 3 camps
            uri, ignore, tag = point_xml.tag[1:].partition("}")
            if tag == 'startpointdescription' or tag == 'endpointdescription':
                # parses the first attributes
                fb_name = point_xml.attrib['id']
                # parse the subscriptions
                self.items_dict[fb_name].parse_subscriptions(point_xml)

    def from_fb(self, fb, fb_xml, point_type='STARTPOINT'):
        if point_type == 'STARTPOINT':
            # creates the start point
            start_point = ua_object.UaObject(self.ua_peer, fb.fb_name, fb.fb_type,
                                             source_type='StartPoint',
                                             browse_name=fb.fb_name,
                                             root_folder='PointSet')
            # parses the xml
            start_point.parse_loop_type_fb(fb, fb_xml)
            # saves the start_point
            self.items_dict[start_point.fb_name] = start_point

        elif point_type == 'ENDPOINT':
            # creates the end point
            endpoint = ua_object.UaObject(self.ua_peer, fb.fb_name, fb.fb_type,
                                          source_type='EndPoint',
                                          browse_name=fb.fb_name,
                                          root_folder='PointSet')
            # parses the xml
            endpoint.parse_service_type_fb(fb, fb_xml)
            # saves the endpoint
            self.items_dict[endpoint.fb_name] = endpoint

    def save_xml(self, xml_set):
        # iterates over the points dictionary
        for point_name, point_value in self.items_dict.items():
            # checks if is a start point
            if point_value.source_type == 'StartPoint':
                # creates a tag with start point value
                point_xml = ETree.SubElement(xml_set, 'startpointdescription')
                # parses the start point
                point_value.save_all_xml(point_xml)

            # checks if is a stop point
            elif point_value.source_type == 'EndPoint':
                # creates a tag with end point value
                point_xml = ETree.SubElement(xml_set, 'endpointdescription')
                # parses the end point
                point_value.save_all_xml(point_xml)
