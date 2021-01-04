import threading
import socket
import queue

from utilities import *


#incoming and outgoing queue are managed by other threads. 

#RESPONSIBILITIES: process messages
class Node(threading.Thread):

    def __init__(self, _id, edges, 
                    links, ntwrk_cnfg, 
                    incoming_queue, 
                    message_manager):

        #extending the thread class
        super().__init__()

        #identifer
        self._id = _id

        #network topology
        self.topology = ntwrk_cnfg

        #state variables
        self.coord_so_far = None
        self.port_to_coord = None
        self.status = 'idle'
        recd_reply = {}

        #connections
        self.edges = edges
        self.links = links
        #self.set_of_ports

        self.in_queue = incoming_queue
        self.msg_mngr = message_manager

    #Defines the logic of the program
    def run(self):
        while True: 
            if not self.in_queue.empty():
                msg = self.in_queue.get()
                if msg['type'] == 'start':
                    for edge in edges:
                        #send a message to node 2
                        #see if a neighboring node has failed
                        msg = msg_mngr.package_msg('alive', edge)
                        self.msg_mngr.send_msg(msg)
                if msg['type'] == 'alive':
                    print(self._id, 'received')
                if msg['type'] == 'fail':
                    print(msg['to_id'], 'failed')
                

    
    
    #def assign_edge(self):
    
    #GET_PORT in the paper
    def set_of_communication_ports(self):
        ports = []
        for edge in self.edges:
            port = self.get_port(edges)
            ports.append(port)
        return ports 

    #return the set of ports for all neighbors 
    def set_of_ports(self):
        ports = []
        for link in self.links:
            port = self.get_port(link)
            ports.append(port)
        return ports

    #returns set of edges (an edge is communication network link)
    def get_port(self, edge):
        return self.topology[edge]['port']

    #returns the port for a node S_j(int) which the node has a link to
    def port_to(self, s_j):
        return self.topology[s_j]['port']

    #INCORRECT; NEEDS REVISION
    #reconfig_node_id = port through which the reconfig message came through
    def sender_of(self, reconfig_node_id):
        return self.port_to(reconfig_node_id)

    #remove_edge(self):

    #reconfig(self, node_list, frag_id):
        #node_list is a FIFO queue
        


#msg_manager will send and package messages on behalf of the node
class Msg_Manager():

    def __init__(self,_id, in_queue, out_queue, ntwrk_confg):

        self.in_queue = in_queue
        self.out_queue = out_queue
        self.topology = ntwrk_confg
        self.id = _id

        port = self.topology[self.id]['port']
        host = self.topology[self.id]['host']
    
    #start, alive, fail, reconfig, no_contension, accepted
    def package_msg(self, msg_type, to_id):
        # message is packaged with a type and the sender's id, host, and port; json string
        msg = {'type': msg_type, 'to_id': to_id, 'from_id':self.id, 'host': host, 'port': port}
        return msg

    def send_msg(self, msg):
        self.out_queue.put(msg)


#the Incoming_Msg_Cntrll will act as a server listening 
#for messages that are 
class Incoming_Msg_Cntrll(threading.Thread):

    def __init__(self, incoming_queue, port, host):
        super().__init__()
        self.in_q = incoming_queue

        
        #construct a socket and listen for incoming messages
        self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.in_socket.bind((host, port))
        self.in_socket.listen()


    #get a message and put it into the queue.
    def run(self):
        while True:

            #establish the connection with the client seeking to send info
            c, addr = self.in_socket.accept()
            #message = c.recv(1024).decode() 

            #should receive a json string to decode
            message = decode(c.recv(1024))

            #FOR TESTING
            if message['type'] == 'start':
                print('Starting!')
                self.in_q.put(message) 
            else:
                self.in_q.put(message)


#MESSGES: types, ports, host (destinations)



#checks the incoming queue for a node to see if there are any
# messages to forward
class Outgoing_Msg_Cntrll(threading.Thread):

    def __init__(self, 
                incoming_queue, 
                outgoing_queue, 
                port, 
                host, 
                ntwrk_cnfg, 
                msg_cm):

        super().__init__()

        self.in_queue = incoming_queue
        self.out_queue = outgoing_queue
        self.port = port
        self.host = host

        self.topology = ntwrk_cnfg

        #socket object to send messages
        self.socket = None
        self.msg_cm = msg_cm

    def run(self):
        while True:
        #check if there are messages to send
            if not self.out_queue.empty():
                msg = self.out_queue.get()
                self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                to_id = msg['to_id']
                port = self.topology[to_id]['port']
                host = self.topology[to_id]['host']
                try: 
                    self.socket.connect((host, port))
                    self.socket.send(encode(msg))
                except socket.error:
                    #couldn't connect; node failure dectected
                    msg = self.msg_cm.package_msg('fail', to_id)
                    self.in_queue.put(msg)



if __name__ == '__main__':        

    #initialize the queues for the node which 
    #are managed by the receiver thread and the sender thread
    incoming_queue = queue.Queue()
    outgoing_queue = queue.Queue()


    #get the file from the command line.
    parser = opt_parser()
    options = parser.parse_args() 


    #load the network topology which holds port, host, 
    #links and edges information for a given node. 
    
    ntwrk_cnfg = load_network_topology(options.topology)

    #populate this node with its id, edges, links, port and host information
    _id = options.id
    host = ntwrk_cnfg[_id]['host']
    port = ntwrk_cnfg[_id]['port']
    links = ntwrk_cnfg[_id]['links']
    edges = ntwrk_cnfg[_id]['edges']

    #initialize the node with its host, links and edges
    #intialize the helper threads
    msg_mngr = Msg_Manager(_id, incoming_queue, outgoing_queue, ntwrk_cnfg)
    in_msg_cntrll = Incoming_Msg_Cntrll(incoming_queue, port, host)
    out_msg_cntrll = Outgoing_Msg_Cntrll(incoming_queue, outgoing_queue, 
                                            port,host, ntwrk_cnfg, msg_mngr)
    node = Node(_id,edges,links, ntwrk_cnfg, incoming_queue, msg_mngr)

    #send a message between (two) three nodes
    in_msg_cntrll.start()
    out_msg_cntrll.start()
    node.start()
