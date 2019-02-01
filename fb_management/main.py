from communication import ide_handler
from fb_management import config_manager
import logging
import sys


if __name__ == "__main__":
    ip = 'localhost'
    port = 61500

    # Configure the logging output
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    config_m = config_manager.ConfigManager()
    hand = ide_handler.Handler(ip, port, 10, config_m)

    try:
        hand.handler()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        hand.stop_server()
        sys.exit(0)

