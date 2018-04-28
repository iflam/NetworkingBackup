from cmd import *
from consts import *

import argparse
import json
import selectors
import socket
import sys

# globals
nodes = [] 
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

def recv(conn):
    print(conn.recv(MAX_READ))

def accept(sock):
    conn, addr = sock.accept()
    print("accepted connection, receiving...")
    packet = json.loads(conn.recv(MAX_READ).decode())
    print(packet)
    nodes.append(addr)
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
    
