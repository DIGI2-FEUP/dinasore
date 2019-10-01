import logging
import os
import sys
import getopt

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from communication import tcp_server
from core import manager

if __name__ == "__main__":
    log_levels = {'ERROR': logging.ERROR,
                  'WARN': logging.WARN,
                  'INFO': logging.INFO}

    address = 'localhost'
    port_diac = 61499
    port_opc = 4840
    log_level = log_levels['ERROR']

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "ha:p:u:l:",
                                   ["address=", "port_diac=", "port_opc=", "log_level"])
    except getopt.GetoptError:
        print('python core/main.py -a <address> -p <port_diac> -u <port_opc> -l <log_level>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python core/main.py -a <address> -p <port_diac> -u <port_opc> -l <log_level>')
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-p", "--port_diac"):
            port_diac = int(arg)
        elif opt in ("-u", "--port_opc"):
            port_opc = int(arg)
        elif opt in ("-l", "--log_level"):
            log_level = log_levels[arg]

    # Configure the logging output
    log_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'error_list.log')
    if os.path.isfile(log_path):
        os.remove(log_path)
    logging.basicConfig(filename=log_path,
                        level=log_level,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    # creates the 4diac manager
    m = manager.Manager()
    # sets the ua integration option
    m.build_ua_manager(address, port_opc, 'data_model.xml')

    # creates the tcp server to communicate with the 4diac
    hand = tcp_server.TcpServer(address, port_diac, 10, m)

    try:
        # handles every client
        while True:
            hand.handle_client()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        hand.stop_server()
        sys.exit(0)
