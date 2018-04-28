# FUSE imports
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
import os

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from cmd import *
from consts import *
from opcodes import *

import argparse
import json
import selectors
import socket
import sys
from memory import Memory

bootstrap_ip = "127.0.0.1" 
bootstrap_sock = None
tier = "basic"
mount = "mnt"
args = None

def intro():
    print("***DiFUSE Client***")
    print("Connected to bootstrap " + bootstrap_ip + " port " + str(args.port))
    print("Type help for a list of commands")

def setup_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip of bootstrap")
    parser.add_argument("-p", "--port", nargs='?', default=1234, type=int, help="port of bootstrap")
    parser.add_argument("-m", "--mount", nargs="?", default="mnt", help="FUSE mount dir")
    parser.add_argument("-t", "--tier", choices=["basic", "hash", "repl"], help="DiFUSE hw tier")
    args = parser.parse_args()

def join():
    global bootstrap_sock
    bootstrap_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bootstrap_sock.connect((bootstrap_ip, args.port))
    packet = new_packet(JOIN)
    bootstrap_sock.send(build(packet))

def new_packet(opcode):
    return {'opcode': opcode}
def build(packet):
    return json.dumps(packet).encode()

def prompt():
    print("DiFUSE Client> ", end='', flush=True)

def help_menu():
    print("help\t show this menu")
    print("bootstrap_ip\t print bootstrap ip")
    print("args.port\t print bootstrap port")

def invalid():
    print("invalid command")

def read(sock):
    print("reading from socket")
    print(bootstrap_sock.recv(MAX_READ))
    # TODO: read packet sent by bootstrap
    pass 

def do_cmd(stdin): 
    cmd = stdin.readline().strip()  
    print("cmd:", cmd)
    if cmd == HELP_CMD:
        help_menu() # help() is python builtin :/
    else: 
        for var, val in list(globals().items()): # iterate through global variables
            if cmd == var:
                print(val)

if __name__ == "__main__":
    setup_args()
    print(args)
    intro()
    join()
    print("Starting FUSE...")
    logging.basicConfig(level=logging.DEBUG)
    if not os.path.exists(args.mount):
        os.makedirs(args.mount)
    fuse = FUSE(Memory(bootstrap_sock), args.mount, foreground=True)
    sel = selectors.DefaultSelector()
    #sel.register(bootstrap_sock, selectors.EVENT_READ, read)
    sel.register(sys.stdin, selectors.EVENT_READ, do_cmd)
    while True:
            prompt()
            events = sel.select()
            for key, mask in events: # dw about mask
                    print(key)
                    callback = key.data
                    callback(key.fileobj)
