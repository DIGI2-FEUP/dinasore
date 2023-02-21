import logging
import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from communication import tcp_server
from core import manager

if __name__ == "__main__":
    log_levels = {'ERROR': logging.ERROR,
                  'WARN': logging.WARN,
                  'INFO': logging.INFO}

    address = 'localhost'
    diac_address = None
    project_name = None
    port_diac = 61499
    port_opc = 4840
    log_level = log_levels['ERROR']
    n_samples = 10
    secs_sample = 20
    monitor = [n_samples, secs_sample]
    agent = False

    help_message = "Usage: python core/main.py [ARGS]\n\n" \
                   " -h, --help: display the help message\n" \
                   " -a, --address: ip address to bind at (default: localhost)\n" \
                   " -p, --port_diac: port for the 4diac communication (default: 61499)\n" \
                   " -l, --log_level: logging level at the file resources/error_list.log\n" \
                   "                  INFO, WARN or ERROR (default: ERROR)"

    # build parser for application command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', metavar='address', nargs=1, help="ip address to bind at (default: localhost)")
    parser.add_argument('-p', metavar='port_diac', nargs=1, type=int, help="port for the 4diac communication "
                                                                           "(default: 61499)")
    parser.add_argument('-l', metavar='log_level', nargs=1,  help="logging level at the file resources/error_list.log, "
                                                                  "e.g. INFO, WARN or ERROR (default: ERROR)")
    # ---------------------

    args = parser.parse_args()

    if args.a != None: address = args.a[0]
    if args.p != None: port_diac = args.p[0]
    if args.l != None: log_level = log_levels[args.l[0]]

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
    m.build_fboot()

    # creates the tcp server to communicate with the 4diac
    hand = tcp_server.TcpServer(address, port_diac, 10, m)
    try:
        # handles every client
        while True:
            hand.handle_client()
    except KeyboardInterrupt:
        logging.info('interrupted server')
        m.stop()
        hand.stop_server()
        sys.exit(0)
