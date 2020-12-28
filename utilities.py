import json
import socket

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


