from opcua import Client
from opc_ua import base
import logging


class UaClient(base.UaBase, Client):

    def __init__(self, address):
        Client.__init__(self, url=address, timeout=60 * 8)
        base.UaBase.__init__(self)
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s][%(threadName)-15s] %(message)s')

        self.connect()
        self.root = self.get_root_node()

        self.subs_dictionary = dict()

    def subscribe(self, path, handler, period=100):
        my_obj = self.root.get_child(path)

        sub = self.create_subscription(period=period, handler=handler)
        handle = sub.subscribe_data_change(my_obj)

        self.subs_dictionary[self.generate_key(path)] = (sub, handle)

    def unsubscribe(self, path):
        (sub, handle) = self.subs_dictionary[self.generate_key(path)]

        sub.unsubscribe(handle)
        sub.delete()

        self.subs_dictionary.pop(self.generate_key(path))

    @staticmethod
    def generate_key(path):
        elements = ""
        for element in path:
            elements.join(["/", element])

        return elements

