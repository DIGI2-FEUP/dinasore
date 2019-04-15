import socket


class READ_VS:

    def schedule(self, event_name, event_value, address, port):
        # OUTPUT EVENTS
        # READ_END - reads operation terminated

        if event_name == 'READ':
            # address = '192.168.0.101'
            # port = 5400

            # Create a TCP/IP socket
            # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            server_address = (address, port)
            # sock.connect(server_address)

            # sock.sendall('insp'.encode('utf-8'))
            # data = sock.recv(2048).decode('utf-8')
            # sock.close()
            data = '2.34,12.32,23.4,green,2.34,12.32,23.4,green'
            return [event_value, data]
