import json
import socket
<<<<<<< HEAD
import argparse

#read arguments from the command line
def opt_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', default=15, type=int)
    parser.add_argument('--topology', default='./ntwk_config.json', type=str)
    return parser

=======
>>>>>>> 64231148f7e43445a0f79f5e4cb260b3fd4c732f

#Function to read the network topology from 
#the json file

def load_network_topology(json_file):
    with open(json_file, 'r') as f:
        fg = json.load(f)
        #hold the graph in a dictionary
        ntwk_topology  = dict()
        for k, i in fg.items():
            ntwk_topology[int(k)] = i
        return ntwk_topology


