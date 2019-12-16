import logging
import os
import sys
import argparse
import glob

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
    n_samples = 10
    secs_sample = 20
    monitor = [n_samples,secs_sample]
    agent = False

    help_message = "Usage: python core/main.py [ARGS]\n\n" \
                   " -h, --help: display the help message\n" \
                   " -a, --address: ip address to bind at (default: localhost)\n" \
                   " -p, --port_diac: port for the 4diac communication (default: 61499)\n" \
                   " -u, --port_opc: port for the opc-ua communication (default: 4840)\n" \
                   " -l, --log_level: logging level at the file resources/error_list.log\n" \
                   "                  INFO, WARN or ERROR (default: ERROR)\n" \
                   " -g, --agent: sets on the self-organizing agent\n" \
                   " -m, --monitor: activates the behavioral anomaly detection feature. \n" \
                   "       If no parameters are specified, the default values are 10 samples\n" \
                   "       for the initial training dataset and each sample with 20 seconds. \n" \
                   "       As an example, you can specify the monitoring parameters in the following way (-m 5 10) \n" \
                   "       meaning 10 samples for training dataset with 10 seconds of monitoring per sample. \n"

    ## build parser for application command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', metavar='address', nargs=1, help="ip address to bind at (default: localhost)")
    parser.add_argument('-p', metavar='port_diac', nargs=1, type=int, help="port for the 4diac communication (default: 61499)")
    parser.add_argument('-u', metavar='port_opc', nargs=1, type=int, help="port for the opc-ua communication (default: 4840)")
    parser.add_argument('-l', metavar='log_level', nargs=1,  help="logging level at the file resources/error_list.log, e.g. INFO, WARN or ERROR (default: ERROR)")
    parser.add_argument('-g', action='store_true', help="sets on the self-organizing agent")
    parser.add_argument('-m', metavar='monitor', nargs='*', help="activates the behavioral anomaly detection feature. If no paramters are specified, the default values are 10 samples for initial training, each sample with 20 seconds (approximately 3m20s). As an example, you can specify paramters the following way (-m 5 10) meaning 10 samples for training with 10 seconds each sample.")
    args = parser.parse_args()

    if args.a != None: address = args.a[0]
    if args.p != None: port_diac = args.p[0]
    if args.u != None: port_opc = args.u[0]
    if args.l != None: log_level = log_levels[args.l[0]]
    agent = args.g
    if args.m != None:
        if len(args.m) == 2:
            monitor=[int(args.m[0]),int(args.m[1])]
        elif len(args.m) == 1 or len(args.m) > 2:
            print("For the monitoring functionality, please specify 2 arguments or none!")
            exit(2)
    else:
        monitor=None

    ##############################################################
    ## remove all files in monitoring folder
    monitoring_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'monitoring','')
    files = glob.glob("{0}*".format(monitoring_path))
    for f in files:
        os.remove(f)
    ##############################################################



    # Configure the logging output
    log_path = os.path.join(os.path.dirname(sys.path[0]), 'resources', 'error_list.log')
    if os.path.isfile(log_path):
        os.remove(log_path)
    logging.basicConfig(filename=log_path,
                        level=log_level,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')

    # creates the 4diac manager
    m = manager.Manager(monitor=monitor)
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
