import logging
import os
import sys
import getopt

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from communication import tcp_server
from core import manager


if __name__ == "__main__":

    address = 'localhost'
    port = 61500

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:p:l:", ["address=", "port="])
    except getopt.GetoptError:
        print('python3 core/main.py -a <address> -p <port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python3 core/main.py -a <address> -p <port>')
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-p", "--port"):
            port = int(arg)

    # Configure the logging output
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    config_m = manager.Manager()
    hand = tcp_server.TcpServer(address, port, 10, config_m)

    try:
        hand.handler()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        hand.stop_server()
        sys.exit(0)
