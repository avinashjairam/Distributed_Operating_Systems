from utilities import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--net_config', default='./ntwk_config.json', type=str)
f = parser.parse_args()

graph = load_network_topology(f.net_config)

print(graph)
