import logging
import os
import sys
import getopt

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from communication import tcp_server
from core import manager

if __name__ == "__main__":

    address = 'localhost'
    port = 61499

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:p:l:", ["address=", "port="])
    except getopt.GetoptError:
        print('python3.6 core/main.py -a <address> -p <port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python3.6 core/main.py -a <address> -p <port>')
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-p", "--port"):
            port = int(arg)

    # Configure the logging output
    log_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'error_list.log')
    if os.path.isfile(log_path):
        os.remove(log_path)
    logging.basicConfig(filename=log_path,
                        level=logging.ERROR,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    # creates the 4diac manager
    m = manager.Manager()
    # sets the ua integration option
    m.build_ua_manager('SMART_COMPONENT', address, 4841, 'data_model_original.xml')

    # creates the tcp server to communicate with the 4diac
    hand = tcp_server.TcpServer(address, port, 10, m)

    try:
        hand.handler()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        hand.stop_server()
        sys.exit(0)
