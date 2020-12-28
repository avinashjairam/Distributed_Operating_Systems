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

        

