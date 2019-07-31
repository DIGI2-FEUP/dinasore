import struct
import socket
import sys
import os


class DiacSimulator:

    def __init__(self, ip_address, bind_port):
        pass
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        self.server_url = (ip_address, bind_port)

    def upload_dinasore(self, file_name):
        # creates the first message
        first_message = self.__build_response(b'<Request ID="0" Action="QUERY"><FB Name="*" Type="*"/></Request>', b'')
        # creates the messages list
        messages_list = [first_message]

        # connects tho the socket
        self.sock.connect(self.server_url)

        # Gets the file path to the fbt (xml) file
        messages_path = os.path.join(sys.path[0], file_name)
        # reads the file
        with open(messages_path) as f:
            content = f.readlines()
        # iterates over the xml of messages
        for row in content:
            message = row.split(';')
            message_text = self.__build_response(message[1].encode('utf-8'), message[0].encode('utf-8'))
            messages_list.append(message_text)

        # sends the configuration
        for msg in messages_list:
            try:
                # Send data
                self.sock.sendall(msg)
                # Look for the response
                data = self.sock.recv(2048)
            except socket.error as msg:
                print(msg)

    @staticmethod
    def __build_response(message_payload, configuration_name):
        # build the first part of the header
        hex_input = '{:04x}'.format(len(configuration_name))
        second_byte = int(hex_input[0:2], 16)
        third_byte = int(hex_input[2:4], 16)
        response_len = struct.pack('BB', second_byte, third_byte)
        response_header_1 = b''.join([b'\x50', response_len])

        # build the second part of the header
        hex_input = '{:04x}'.format(len(message_payload))
        second_byte = int(hex_input[0:2], 16)
        third_byte = int(hex_input[2:4], 16)
        response_len = struct.pack('BB', second_byte, third_byte)
        response_header_2 = b''.join([b'\x50', response_len])

        # join the 3 parts
        response = b''.join([response_header_1, configuration_name, response_header_2, message_payload])
        return response


# diac = DiacSimulator('localhost', 61499)
# diac.upload_dinasore('opc_ua_FORTE_PC.fboot')
