from cmd import *
from consts import *
from opcodes import *
import packets

import argparse
import json
import selectors
import socket
import sys

# globals
nodes = [] 
files = {} # dict mapping files to nodes 
args = None

sel = selectors.DefaultSelector() # need to select between accept, recv, and input

def intro():
    print("***DiFUSE Bootstrap***")
    print("Type help for a list of commands")

def prompt():
    print("DiFUSE Bootstrap> ", end='', flush=True)

def help_menu():
    print("help\t show this menu")
    print("nodes\t print number of nodes in network")

def invalid():
    print("invalid command")

# close a socket and unregister from select
# don't remove from nodes list, bc node may still be in network, just not currently talking to bootstrap
def close(conn):
    conn.close()
    sel.unregister(conn)

def recv(conn):
    print('Receiving from', conn)
    packet = packets.unpack(conn.recv(MAX_READ))
    print('Received', packet)
    if not packet:
        print('Empty packet, closing connection to', conn)
        close(conn)
        return
    if 'opcode' not in packet:
        print('Invalid packet: opcode missing')

    if packet['opcode'] == OP_JOIN:
        nodes.append(packet['loc'])

    elif packet['opcode'] == OP_LS:
        print('Received OP_LS')
        reply = packets.new_packet(OP_LS_R)
        reply['ls'] = list(files.keys())
        conn.send(packets.build(reply))

    elif packet['opcode'] == OP_CREATE:
        print('Creating file')
        files[packet['path']] = packet['loc'] # map new file to node

    elif packet['opcode'] == OP_FIND: 
        print('Received OP_FIND', packet)
        reply = packets.new_packet(OP_FIND_R)
        if packet['path'] in files:
            reply['loc'] = files[packet['path']] 
        # TODO: error file not found
        print('Sending OP_FIND_R', reply)
        conn.send(packets.build(reply))

    elif packet['opcode'] == OP_BYE:
        print('Received OP_LEAVE', packet)
        print('nodes are: ', nodes)
        if packet['loc'] in nodes:
            nodes.remove(packet['loc'])
        temp = {x:y for x,y in files.items()}
        for f in temp:
            print(packet['loc'])
            print(temp[f])
            if temp[f] == packet['loc']:
                del files[f]
        reply = packets.new_packet(OP_BYE_R)
        print('Sending OP_LEAVE_R', reply)
        print('Sending to: ',conn)
        conn.send(packets.build(reply))

    else:
        print('Invalid opcode')

def accept(sock):
    conn, addr = sock.accept()
    print('accepted connection', conn)
    sel.register(conn, selectors.EVENT_READ, recv) 

def do_cmd(stdin): 
    cmd = stdin.readline().strip()	
    print("cmd:", cmd)
    if cmd == HELP_CMD:
        help_menu() # help() is python builtin :/
    else: 
        for var, val in list(globals().items()): # iterate through global variables
            if cmd == var:
                print(val)

def setup_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", nargs='?', type=int, default=1234, help="port of bootstrap")
    parser.add_argument("-t", "--tier", choices=["basic", "hash", "repl"], help="DiFUSE hw tier")
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    setup_args()
    intro()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", args.port))
    sock.listen(1) # listen for nodes
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept) 
    sel.register(sys.stdin, selectors.EVENT_READ, do_cmd)
    while True:
        prompt()
        events = sel.select()
        for key, mask in events: # dw about mask
            callback = key.data
            callback(key.fileobj)
    
