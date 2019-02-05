import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from communication import tcp_server
from core import manager


if __name__ == "__main__":
    ip = 'localhost'
    port = 61500

    # Configure the logging output
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    config_m = manager.Manager()
    hand = tcp_server.Handler(ip, port, 10, config_m)

    try:
        hand.handler()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        hand.stop_server()
        sys.exit(0)
