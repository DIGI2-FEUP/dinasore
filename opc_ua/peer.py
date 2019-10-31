from opc_ua import client
from opc_ua import base
from opcua import Server
import threading
import logging


class UaPeer(Server, base.UaBase):

    def __init__(self, address, server_name='systec_ua'):
        Server.__init__(self)
        base.UaBase.__init__(self)

        logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s][%(threadName)-15s] %(message)s')

        self.set_endpoint(address)
        self.set_server_name(server_name)

        # setup our own namespace, not really necessary but should as spec
        self.uri = "http://systec.fe.up.pu"
        self.register_namespace(self.uri)

        self.root = self.get_root_node()

        self.lock = threading.Lock()
        self.client_dictionary = dict()

        self.start()

    def add_client(self, client_address):
        self.lock.acquire()
        if client_address not in self.client_dictionary:
            c = client.UaClient(client_address)
            self.client_dictionary[client_address] = c
        self.lock.release()

    def remove_client(self, client_address):
        self.lock.acquire()
        c = self.client_dictionary[client_address]
        c.disconnect()
        self.client_dictionary.pop(client_address)
        self.lock.release()

    def remove_all_clients(self):
        self.lock.acquire()
        for address, c in self.client_dictionary.items():
            c.disconnect()
        self.client_dictionary.clear()
        self.lock.release()

    def client_read(self, client_address, path):
        self.lock.acquire()
        val = self.client_dictionary[client_address].read(path)
        self.lock.release()
        return val

    def client_write(self, client_address, path, val):
        self.lock.acquire()
        self.client_dictionary[client_address].write(path, val)
        self.lock.release()

    def client_call_method(self, client_address, path, *args):
        self.lock.acquire()
        result = self.client_dictionary[client_address].call_method(path.copy(), *args)
        self.lock.release()
        return result
