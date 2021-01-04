import socket

from utilities import *

if __name__ == '__main__':

    parser = opt_parser()
    options = parser.parse_args()

    ntwrk_cnfg = load_network_topology(options.topology)
    begin(options.id, options.failed, ntwrk_cnfg)
