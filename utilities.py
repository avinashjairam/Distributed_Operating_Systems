import json
import socket
import argparse

#read arguments from the command line
def opt_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', default=15, type=int)
    parser.add_argument('--topology', default='./ntwk_config.json', type=str)
    return parser

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


#messages are sent via json strings
def encode(msg):
    json_str = json.dumps(msg)
    return bytes(json_str, 'utf-8')

def decode(msg):
    answer = json.loads(msg.decode('utf-8'))
    return answer

def begin(_id, topology):
    port = topology[_id]['port']
    host = topology[_id]['host']
    
    start_msg = {'type': 'start'}

    #send a start message to start the exchange of messages
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(encode(start_msg))

    
    
