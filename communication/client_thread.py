import threading
import logging


class ClientThread(threading.Thread):

    def __init__(self, connection, client_address, config_m):
        threading.Thread.__init__(self, name='{0}:{1}'.format(client_address[0], client_address[1]))

        self.config_m = config_m
        self.connection = connection
        self.client_address = client_address

    def run(self):
        try:
            logging.info('connection from {0}'.format(self.client_address))

            # Receive the data in small chunks and retransmit it
            while True:
                data = self.connection.recv(2048)
                logging.info('received {0}'.format(data))

                if data:
                    response = self.parse_request(data)
                    logging.info('sending response {0}'.format(response))
                    self.connection.sendall(response)

                else:
                    logging.info('no more data from {0}'.format(self.client_address))
                    break

        finally:
            # Clean up the connection
            self.connection.close()

    def parse_request(self, data):
        data_str = data.decode('utf-8')
        xml_data = data_str[data_str.find('<Request'):]
        request_header = data_str[:data_str.find('<Request')]
        config_id_size = int(data[1:3].hex(), 16)

        if config_id_size == 0:
            response = self.config_m.parse_configuration(xml_data)
        else:
            config_id = request_header[3: config_id_size + 3]
            response = self.config_m.parse_payload(xml_data, config_id)

        return response
