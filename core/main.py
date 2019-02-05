from communication import tcp_server
from core import manager
import logging
import sys


if __name__ == "__main__":
    ip = 'localhost'
    port = 61500

    # Configure the logging output
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    config_m = manager.ConfigManager()
    hand = tcp_server.Handler(ip, port, 10, config_m)

    try:
        hand.handler()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        hand.stop_server()
        sys.exit(0)

