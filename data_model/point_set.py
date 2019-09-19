from data_model import utils
from data_model import ua_base
import xml.etree.ElementTree as ETree


class PointSet:

    def __init__(self, ua_peer):
        self.points_dict = dict()
        # receives the peer methods to add the opc-ua objects
        self.__ua_peer = ua_peer
        # dictionary who stores the points
        self.points_dict = dict()

        # creates the opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'PointSet')

    def parse_xml_startpoint(self, item_xml):
        for point_xml in item_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = point_xml.tag[1:].partition("}")
            if tag == 'startpointdescription':
                # gets the attributes
                fb_name = point_xml.attrib['id']
                fb_type = point_xml.attrib['dId']
                # creates the start point
                start_point = ua_base.UaBaseLayer2(self.__ua_peer, fb_name, fb_type, 'PointSet', 'StartPoint')
                # parses the xml
                start_point.parse_loop_type_xml(point_xml)
                # saves the endpoint
                self.points_dict[fb_name] = start_point

    def parse_xml_endpoint(self, item_xml):
        for point_xml in item_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = point_xml.tag[1:].partition("}")
            if tag == 'endpointdescription':
                # gets the attributes
                fb_name = point_xml.attrib['id']
                fb_type = point_xml.attrib['dId']
                # creates the endpoint
                end_point = ua_base.UaBaseLayer2(self.__ua_peer, fb_name, fb_type, 'PointSet', 'EndPoint')
                # parses the xml
                end_point.parse_service_type_xml(point_xml)
                # saves the endpoint
                self.points_dict[fb_name] = end_point

    def from_fb(self, fb, fb_xml, point_type='STARTPOINT'):
        if point_type == 'STARTPOINT':
            # creates the start point
            start_point = ua_base.UaBaseLayer2(self.__ua_peer, fb.fb_name, fb.fb_type, 'PointSet', 'StartPoint')
            # parses the xml
            start_point.parse_loop_type_fb(fb, fb_xml)
            # saves the start_point
            self.points_dict[start_point.fb_name] = start_point

        elif point_type == 'ENDPOINT':
            # creates the end point
            endpoint = ua_base.UaBaseLayer2(self.__ua_peer, fb.fb_name, fb.fb_type, 'PointSet', 'EndPoint')
            # parses the xml
            endpoint.parse_service_type_fb(fb, fb_xml)
            # saves the endpoint
            self.points_dict[endpoint.fb_name] = endpoint

    def save_xml(self, xml_set):
        # iterates over the points dictionary
        for point_name, point_value in self.points_dict.items():
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
