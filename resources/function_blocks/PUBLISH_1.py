import socket
import struct


class PUBLISH_1:

    def __init__(self):
        self.QO = None
        self.pair = None
        # Create the datagram socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def schedule(self, event_name, event_value, QI, ID, SD_1):
        self.QO = QI
        if event_name == 'INIT':
            return self.init(event_value, ID)

        elif event_name == 'REQ':
            return self.request(event_value, SD_1)

    def init(self, event_value, ID):
        # Set a timeout so the socket does not block indefinitely when trying
        # to receive data.
        self.sock.settimeout(0.2)
        # Set the time-to-live for messages to 1 so they do not go past the
        # local network segment.
        ttl = struct.pack('b', 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        self.pair = ID.split(':')

        return [event_value, None, self.QO, None]

    def request(self, event_value, SD_1):
        message = str(1).encode(encoding='utf-8')
        self.sock.sendto(message, (self.pair[0], int(self.pair[1])))

        return [None, event_value, self.QO, None]
