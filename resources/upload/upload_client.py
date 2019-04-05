import socket
import sys
import os
import getopt
import struct
import time
import xml.etree.ElementTree as ETree

if __name__ == "__main__":
    time.sleep(0.5)

    address = 'localhost'
    port = 61499
    file_name = 'HUMIDITY.xml'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:p:l:", ["address=", "port="])
    except getopt.GetoptError:
        print('python3.6 resources/upload/upload_client.py -a <address> -p <port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python3.6 resources/upload/upload_client.py -a <address> -p <port>')
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-p", "--port"):
            port = int(arg)

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (address, port)
    sock.connect(server_address)

    # Gets the file path to the fbt (xml) file
    messages_path = os.path.join(sys.path[0], file_name)
    # Reads the xml
    tree = ETree.parse(messages_path)
    # Gets the root element
    root = tree.getroot()

    messages = [b'\x50\x00\x00\x50\x00\x4e'
                b'<Request ID="0" Action="QUERY"><FB Name="*" Type="*"/></Request>',
                b'\x50\x00\x00\x50\x00\x4e'
                b'<Request ID="1" Action="CREATE"><FB Name="EMB_RES" Type="EMB_RES" /></Request>']

    for request_xml in root:
        request_payload = ETree.tostring(request_xml)
        hex_input = '{:04x}'.format(len(request_payload))
        second_byte = int(hex_input[0:2], 16)
        third_byte = int(hex_input[2:4], 16)
        request_len = struct.pack('BB', second_byte, third_byte)
        request_header = b''.join([b'\x50\x00\x07EMB_RES\x50', request_len])

        request = b''.join([request_header, request_payload])

        messages.append(request)

    for msg in messages:
        try:
            # Send data
            # print('sending {0}'.format(msg))
            sock.sendall(msg)

            # Look for the response
            data = sock.recv(2048)
            # print('received {0}'.format(data))

        except socket.error as msg:
            print(msg)

    # print('closing socket')
    sock.close()
