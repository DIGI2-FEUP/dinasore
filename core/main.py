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
    agent = False

    help_message = "Usage: python core/main.py [ARGS]\n\n" \
                   " -h, --help: display the help message\n" \
                   " -a, --address: ip address to bind at (default: localhost)\n" \
                   " -p, --port_diac: port for the 4diac communication (default: 61499)\n" \
                   " -u, --port_opc: port for the opc-ua communication (default: 4840)\n" \
                   " -l, --log_level: logging level at the file resources/error_list.log\n" \
                   "                  INFO, WARN or ERROR (default: ERROR)\n" \
                   " -g, --agent: sets on the self-organizing agent\n\n"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "h:a:p:u:l:g:",
                                   ["help", "address", "port_diac", "port_opc", "log_level", "agent"])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_message)
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-p", "--port_diac"):
            port_diac = int(arg)
        elif opt in ("-u", "--port_opc"):
            port_opc = int(arg)
        elif opt in ("-l", "--log_level"):
            log_level = log_levels[arg]
        elif opt in ("-g", "--agent"):
            agent = True

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
        m.manager_ua.stop_ua()
        hand.stop_server()
        sys.exit(0)
