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
import packets
import socks

import argparse
import json
import selectors
import signal
import socket
import sys
import threading
from memory import Memory

bootstrap_ip = "127.0.0.1" 
bootstrap_sock = None
listen_sock = None
tier = "basic"
mount = "mnt"
filesystem = None
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

# join the network
# global listen_sock is where this node will accept connections from other nodes (incl. bootstrap)
# temp_sock used to send bootstrap join request with addr of listen_sock, then closed
def join():
    global listen_sock
    listen_sock = socks.listen_sock() 
    listen_sock.setblocking(False)
    temp_sock = socks.tcp_sock() # only a temp sock is required to join network
    temp_sock.connect((bootstrap_ip, args.port))
    print('connected to bootstrap', temp_sock)
    packet = packets.join_packet(listen_sock.getsockname())
    print('Sending join request', packet)
    temp_sock.send(packets.build(packet))
    #TODO: recv ack?
    temp_sock.close()

def prompt():
    print("DiFUSE Client> ", end='', flush=True)

def help_menu():
    print("help\t show this menu")
    print("bootstrap_ip\t print bootstrap ip")
    print("args.port\t print bootstrap port")

def invalid():
    print("invalid command")

def accept(sock):
    conn, addr = sock.accept()
    print('accepted connection')
    sel.register(conn, selectors.EVENT_READ, read)

def close(sock):
    sel.unregister(sock)
    sock.close()

def read(sock):
    print("reading from socket")
    packet = packets.unpack(sock.recv(MAX_READ))
    print(packet)
    if not packet:
        print('Read empty packet, closing connection', sock)
        close(sock)
        return
    if packet['opcode'] == OP_SYSCALL:
        # TODO: do syscall
        print('Received OP_SYSCALL')
        reply = packets.new_packet(OP_SYSCALL_R)
        print('syscall', packet['syscall'])
        if packet['syscall'] == 'getattr': 
            reply['getattr'] = filesystem.getattr(packet['path'])
        else:
            print('Invalid syscall')
        print('Sending OP_SYSCALL_R', reply)
        sock.send(packets.build(reply))
    else:
        print('Invalid opcode')

def do_cmd(stdin): 
    cmd = stdin.readline().strip()  
    print("cmd:", cmd)
    if cmd == HELP_CMD:
        help_menu() # help() is python builtin :/
    else: 
        for var, val in list(globals().items()): # iterate through global variables
            if cmd == var:
                print(val)

def fuse_thread():
    global filesystem
    filesystem = Memory((bootstrap_ip, args.port), listen_sock.getsockname())
    fuse = FUSE(filesystem, args.mount, foreground=True)

if __name__ == "__main__":
    setup_args()
    print(args)
    intro()
    join()
    print("Starting FUSE...")
    #logging.basicConfig(level=logging.DEBUG)
    threading.Thread(target=fuse_thread, name='fuse_thread').start()
    if not os.path.exists(args.mount):
        os.makedirs(args.mount)
    sel = selectors.DefaultSelector()
    #sel.register(bootstrap_sock, selectors.EVENT_READ, read)
    sel.register(sys.stdin, selectors.EVENT_READ, do_cmd)
    sel.register(listen_sock, selectors.EVENT_READ, accept)
    while True:
            prompt()
            events = sel.select()
            for key, mask in events: # dw about mask
                    print(key)
                    callback = key.data
                    callback(key.fileobj)
