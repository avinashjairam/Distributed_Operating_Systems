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
        self.recd_reply = {}

        #connections
        self.edges = edges
        self.links = links
        #self.set_of_ports

        self.in_queue = incoming_queue
        self.msg_mngr = message_manager
        self.failed_node = None

    #Defines the logic of the program
    def run(self):
        print('node', self._id, 'starting')
        while True: 
            if not self.in_queue.empty():
                msg = self.in_queue.get()
                print(msg)
                if msg['type'] == 'start':
                    for edge in edges:
                        print(edge)
                        #send a message to node 2
                        #see if a neighboring node has failed
                        new_msg = self.msg_mngr.package_msg('alive', edge, None, None, None)
                        self.msg_mngr.send_msg(new_msg)
                #MAY NOT NEED THIS; MAY INDUCE A PROBLEM
                if msg['type'] == 'alive':
                    print('node', msg['from_id'], 'is alive' )
                if msg['type'] == 'fail':
                    print(msg['to_id'], 'failed')
                    #we should change the topology so we don't send messages to the failed node.
                    #DO WE SIMPLY REMOVE IT FROM THE TOPOLOGY?
                    #NEED TO AVOID THE FAILED NODE
                    self.failed_node = msg['to_id']

                    #send a reconfig message and start a reconfiguration
                    #NODE_LIST LIFO data structure
                    node_list = [self._id]
                    frag_id = self._id
                    
                    self.coord_so_far = self._id

                    for link in self.links:
                        if link != self.failed_node:
                            new_msg = self.msg_mngr.package_msg('reconfig', link, node_list, frag_id, self.failed_node)
                            self.msg_mngr.send_msg(new_msg)
                    self.status = 'waiting'
                
                if msg['type'] == 'reconfig':
                    print('node', self._id, 'start reconfig.')
                    node_list = msg['node_list']
                    frag_id = msg['frag_id']
                    self.reconfig(msg, node_list, frag_id)
                    print('here')

                if msg['type'] == 'no_contention':
                    sender_id = int(msg['from_id'])
                    if sender_id in self.recd_reply.keys():
                        self.recd_reply[sender_id] = 'no_contention'
                    if not self.there_is_a_none(self.recd_reply):
                        self.all_nodes_responde()

                if msg['type'] == 'accepted':
                    sender_id = int(msg['from_id'])
                    if sender_id in self.recd_reply.keys():
                        self.recd_reply[sender_id] = 'accepted'
                    if not self.there_is_a_none(self.recd_reply):
                        self.all_nodes_responde()

                if msg['type'] == 'stop':
                    sender_id = int(msg['from_id'])
                    frag_id = msg['frag_id']
                    e = self.sender_of(sender_id)
                    if frag_id > self.coord_so_far:
                        self.coord_so_far = frag_id
                        if self.port_to_coord is not None:
                            # Sending 'stop' message to the sender of the reconfig message
                            new_msg = self.msg_mngr.package_msg('stop', e_id, None, frag_id, None)
                            self.msg_mngr.send_msg(new_msg)
                        self.port_to_coord = e
                    if frag_id == self.coord_so_far:
                        if self.port_to_coord not in self.set_of_communication_ports():
                            if self.port_to_coord is not None:
                                # Send a 'no_contention' msg through port_to_coord
                                new_msg = self.msg_mngr.package_msg('no_contention', e_id, None, None, None)
                                self.msg_mngr.send_msg(new_msg)
                            self.recd_reply[self.port_to_coord] = 'no_contention'
                            if not self.there_is_a_none(self.recd_reply):
                                self.all_nodes_responde()
                        else:
                            # Sending 'stop' message to the sender of the reconfig message
                            new_msg = self.msg_mngr.package_msg('stop', e_id, None, frag_id, None)
                            self.msg_mngr.send_msg(new_msg)
                            self.port_to_coord = e
                    if frag_id < self.coord_so_far:
                        # Sending 'stop' message to the sender of the reconfig message
                        new_msg = self.msg_mngr.package_msg('stop', e_id, None, self.coord_so_far, None)
                        self.msg_mngr.send_msg(new_msg)








    def there_is_a_none(self, d):
        for item in d.items():
            if item is None:
                return True
        return False

    def assign_edge(self, to_id):
        self.edges.append(to_id)

    
    #GET_PORT in the paper
    def set_of_communication_ports(self):
        ports = []
        for edge in self.edges:
            port = self.get_port(edge)
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

    def reconfig(self, msg, node_list, frag_id):
        #node_list is a LIFO queue

        if self.status == 'idle':
            self.coord_so_far = frag_id
            self.status = 'wait'
            self.port_to_coord = self.sender_of(msg['from_id'])
            node_list.append(self._id)

            self.failed_node = msg['failed_node']
            #we don't need the ports here. We just need to know the id of the links for the node, which we have.
            #link != self.frag_id WRONG. More likely id of port_to_cord 
            for link in self.links:
                if link != self.failed_node and link != frag_id:
                    #NEED TO CHANGE FRAG_ID?
                    new_msg = self.msg_mngr.package_msg('reconfig', link, node_list, frag_id, self.failed_node)
                    self.msg_mngr.send_msg(new_msg)

        
 
        if self.status == 'wait':
            e = self.sender_of(msg['from_id'])
            e_id = int(msg['from_id'])

            # Message that received earlier
            if frag_id == self.coord_so_far and e not in self.set_of_communication_ports():

            # I did not pass any other information in contention.
            # send 'NO_CONTENTION' through port e(I'm not sure I sent the msg through port e)
            # need the id of e 

                msg = self.msg_mngr.package_msg('no_contention', e_id, None, None, None)
                self.msg_mngr.send_msg(msg)
            # Detect a loop
            if self._id in node_list:
                #need to send no-contension back 
                msg = self.msg_mngr.package_msg('no_contention', e_id, None, None, None)
                self.msg_mngr.send_msg(msg)

            # Resolve contention
            if (self.coord_so_far > frag_id) or ((self.coord_so_far == frag_id) and (self._id > e_id)):
                # Sending 'stop' message to the sender of the reconfig message
                msg = self.msg_mngr.package_msg('stop', e_id, None, self.coord_so_far, None)
                self.msg_mngr.send_msg(msg)
            else:
                self.coord_so_far = frag_id
                if self.port_to_coord is not None:
                    # Sending 'stop' message to the sender of the reconfig message
                    msg = self.msg_mngr.package_msg('stop', e_id, None, frag_id, None)
                    self.msg_mngr.send_msg(msg)
                self.port_to_coord = e


    def all_nodes_responde(self):
        responses = list(self.recd_reply.values())
        if 'accepted' in responses:
            if self.port_to_coord is not None:
                # send a msg through port_to_coord
                msg = self.msg_mngr.package_msg('accepted', None, None, None, None)
                self.msg_mngr.send_msg(msg)
            if self.port_to_coord not in self.set_of_communication_ports():
                if self.port_to_coord is not None:
                    self.assign_edge(self.port_to_coord)

        else:
            if (self.port_to_coord not in self.set_of_communication_ports()) and len(set(self.set_of_ports()).difference(set([self.port_to_coord])).intersection(set(self.set_of_communication_ports()))) != 0:
                if self.port_to_coord is not None:
                    self.assign_edge(self.port_to_coord)
                    # send a msg through port_to_coord
                    msg = self.msg_mngr.package_msg('accepted', None, None, None, None)
                    self.msg_mngr.send_msg(msg)
            else:
                if self.port_to_coord is not None:
                    # send a 'no_contention' msg through port_to_coord
                    msg = self.msg_mngr.package_msg('no_contention', None, None, None, None)
                    self.msg_mngr.send_msg(msg)

        self.status = 'idle'
        print('node', self._id, 'finished')
        self.recd_reply = {}


         
        


#msg_manager will send and package messages on behalf of the node
class Msg_Manager():

    def __init__(self,_id, in_queue, out_queue, ntwrk_confg):

        self.in_queue = in_queue
        self.out_queue = out_queue
        self.topology = ntwrk_confg
        self.id = _id

        port = self.topology[self.id]['port']
        host = self.topology[self.id]['host']
    
    #TYPES: start, alive, fail, reconfig, no_contension, accepted, stop
    def package_msg(self, msg_type, to_id, node_list, frag_id, failed_node):
        # message is packaged with a type and the sender's id, host, and port; json string
        msg = {'type': msg_type, 
                'to_id': to_id, 
                'from_id':self.id, 
                'host': host, 
                'port': port,
                'node_list': node_list,
                'frag_id': frag_id, 
                'failed_node': failed_node }
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
            #if message['type'] == 'start':
            #    print('Starting!')
            #    self.in_q.put(message) 
            #error occurs here
            #else:
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
                    #ALSO NEED TO DETECT A FAILURE ONCE
                    msg = self.msg_cm.package_msg('fail', to_id, None, None, None)
                    self.in_queue.put(msg)

                    #Use an If statement to make sure you do not send a message to a
                    #failed node.



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
