from data_model import utils
from data_model import point
import xml.etree.ElementTree as ETree


class PointSet(utils.UaInterface):

    def __init__(self, ua_peer):
        self.points_dict = dict()
        # receives the peer methods to add the opc-ua objects
        self.__ua_peer = ua_peer
        # dictionary who stores the points
        self.points_dict = dict()

        # creates the opc-ua folder
        utils.default_folder(self.__ua_peer, self.__ua_peer.base_idx,
                             self.__ua_peer.ROOT_PATH, self.__ua_peer.ROOT_LIST, 'PointSet')

    def from_xml(self, item_xml):
        for point_xml in item_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = point_xml.tag[1:].partition("}")

            if tag == 'endpointdescription':
                # gets the attributes
                fb_name = point_xml.attrib['name']
                fb_type = point_xml.attrib['type']
                # creates the endpoint
                end_point = point.Point(self.__ua_peer, fb_name, fb_name, fb_type, 'ENDPOINT')
                # parses the xml
                end_point.from_xml(point_xml)
                # saves the endpoint
                self.points_dict[fb_name] = end_point

            elif tag == 'startpointdescription':
                # gets the attributes
                fb_name = point_xml.attrib['name']
                fb_type = point_xml.attrib['type']
                # creates the start point
                start_point = point.Point(self.__ua_peer, fb_name, fb_name, fb_type, 'STARTPOINT')
                # parses the xml
                start_point.from_xml(point_xml)
                # saves the endpoint
                self.points_dict[fb_name] = start_point

    def from_fb(self, fb, fb_xml, point_type=''):
        if point_type == 'STARTPOINT':
            # creates the start point
            start_point = point.Point(self.__ua_peer, fb.fb_name, fb.fb_name, fb.fb_type, 'STARTPOINT')
            # parses the xml
            start_point.from_fb(fb, fb_xml)
            # saves the start_point
            self.points_dict[start_point.fb_name] = start_point

        elif point_type == 'ENDPOINT':
            # creates the end point
            endpoint = point.Point(self.__ua_peer, fb.fb_name, fb.fb_name, fb.fb_type, 'ENDPOINT')
            # parses the xml
            endpoint.from_fb(fb, fb_xml)
            # saves the endpoint
            self.points_dict[endpoint.fb_name] = endpoint

    def save_xml(self, xml_set):
        # iterates over the points dictionary
        for point_name, point_value in self.points_dict.items():
            # checks if is a start point
            if point_value.fb_general_type == 'STARTPOINT':
                # creates a tag with start point value
                point_xml = ETree.SubElement(xml_set, 'startpointdescription')
                # parses the start point
                point_value.save_xml(point_xml)

            # checks if is a stop point
            elif point_value.fb_general_type == 'ENDPOINT':
                # creates a tag with end point value
                point_xml = ETree.SubElement(xml_set, 'endpointdescription')
                # parses the end point
                point_value.save_xml(point_xml)

    def create_ua_connection(self, source, destination, fb):
        # splits both source and destination (fb, fb_variable)
        source_attr = source.split(sep='.')
        destination_attr = destination.split(sep='.')

        point_item = self.points_dict.get(fb.fb_type)
        # checks if the destination is a variable (not event)
        if (point_item.fb_general_type == 'ENDPOINT') and (destination_attr[1] in fb.input_vars):
            # builds the node_id for the source
            node_id = '{0}:Variables:{1}'.format(source_attr[0], source_attr[1])
            # creates the subscription at the instance
            point_item.create_ua_connection(source_node=node_id, destination_variable=destination_attr[1])
