<<<<<<< HEAD
import threading
import socket
import queue

from utilities import *


#incoming and outgoing queue are managed by other threads. 


class Node(threading.Thread):

    def __init__(self, _id, edges, links):
        #extending the thread class
        super().__init__()

        #identifer
        self._id = _id

        #state variables
        self.coord_so_far = None
        self.port_to_coord = None
        self.status = 'idle'
        recd_reply = {}

        #connections
        self.edges = edges
        self.links = links
        #self.ports

    def run(self):
        print(self._id)
        print(self.edges)
        print(self.links)

    #def assign_edge(self):

    #def set_of_ports(self):

    #def get_port(self):

    #port_to(self):

    #sender_of(self):

    #remove_edge(self):

    #reconfig(self):


#the Incoming_Msg_Cntrll will act as a server listening 
#for messages that are 
class Incoming_Msg_Cntrll(threading.Thread):

    def __init__(self, incoming_queue, port, host):
        super().__init__()
        self.in_q = incoming_queue

        
        #construct a socket and listen for incoming messages
        in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        in_socket.bind(host, port)
        in_socket.listen()


    #get a message and put it into the queue.
    def run(self):
        #while True:

        #establish the connection with the client seeking to send info
        c, addr = in_socket.accept()
        message = c.recv(1024)

        #FOR TESTING
        if message == 'hello':
            c.sendall('hello')

        #if the message is either failure or reconfig
        self.in_q.put(message) 



#checks the incoming queue for a node to see if there are any
# messages to forward
class Sending_Msg_Cntrll(threading.Thread):

    def __init__(self, incoming_queue, outgoing_queue, port, host):
        super().__init__()

        self.in_queue = incoming_queue
        self.out_queue = outgoing_queue
        self.port = port
        self.host = host

        #socket object to send messages
        self.socket = None

    def run(self):
        #check if there are messages to send
        if  




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
    node = Node(_id,edges,links)


    #send a message between (two) three nodes
    #node.start()


=======
#node.py abstracts the functionality of a computing agent
#in the network. It is divided into three main threads:
# 1) a Receiver class to manage messages coming into the node
# 2) a Sender class to manage messages that are leaving the node
# 3) a Node class which provides the main function, Reconfig(), and
# processes the messages it receives accordingly.
# 4) Message_controller constructs the message object, which keeps track
# of the node sending the message, the node receiving the message and the type 
# of message being sent. 

import threading
import socket
import queue 

from utlilties import *

class Receiver(threading.Thread):

    def __init__(self, host, port, queue):
        super().__init__()

        # maintain a socket for the receiving of messages
        self._socket = socket(socket.AF_INET, socket.sock_stream)
        self._socket.bind((port, host))
        self._socket.listen()
        
        # upon receiving a message put it in a queue

        self._queue = queue

    # overwrite the run() function for this thread
    def run(self):
        while True:
            #receive any data that comes through the socket

            # translate and process the data 






class Message_Controller(object):

    def __init__(self, graph, incoming, outgoing, ID):

        self._graph = graph
        self._incoming = incoming
        self._outgoing = outgoing
        self._id = ID

    def direct_message(self, ID, message):
        message['host'] = self._graph[ID]['host']
        message['port'] = self._graph[ID]['port']

        message['to_id'] = ID
        message['id'] = self._id

    def messages_to_send(self):
        return not self._incoming.empty()

    def get_messages(self):
        return self._incoming.get()


class Node(threading.Thread):

    def __init__(self, ID, links, edges, msg_contlr):
        super().__init__()
        self.setName('Node ' + ID)

        self._msg_contlr = msg_contlr
        
        #state variables 

        self.coord_so_far = self.ID
        self.port_to_coord = None
        self.recd_reply = {}
        self.status = 'idle'

        #for each node in the graph, maintain its links, ports, and edges

        self._ports
        self._edges 

        
>>>>>>> 64231148f7e43445a0f79f5e4cb260b3fd4c732f

