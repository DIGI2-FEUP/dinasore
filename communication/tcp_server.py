import socket
import logging
import sys
from communication import client_thread


class TcpServer:

    def __init__(self, ip, port, limit_connections, config_m):
        self.config_m = config_m

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (ip, port)
        logging.info('starting up on %s port %s' % server_address)

        # Reuse the socket address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind(server_address)
        except socket.error as msg:
            logging.error('bind failed.')
            logging.error(msg)
            sys.exit()

        # Listen for incoming connections
        self.sock.listen(limit_connections)

    def handle_client(self):
        # Wait for a connection
        logging.info('waiting for a connection...')
        connection, client_address = self.sock.accept()

        thread = client_thread.ClientThread(connection, client_address, self.config_m)
        thread.start()

    def stop_server(self):
        self.sock.close()
