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
t = None
fuse = None
sel = selectors.DefaultSelector()
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
    try:
        temp_sock.connect((bootstrap_ip, args.port))
    except:
        print("Could not connect to " + str(bootstrap_ip) + " on port " + str(args.port))
        sys.exit(0)
    print('connected to bootstrap', temp_sock)
    packet = packets.join_packet((socket.gethostbyname(socket.gethostname()),listen_sock.getsockname()[1]))
    print('Sending join request', packet)
    temp_sock.send(packets.build(packet))
    #TODO: recv ack?
    temp_sock.close()

def leave():
    global listen_sock
    temp_sock = socks.tcp_sock()
    temp_sock.connect((bootstrap_ip,args.port))
    print('connected to bootstrap for exit', temp_sock)
    packet = packets.leave_packet(listen_sock.getsockname())
    print('sending leave notice', packet)
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
    print('accepted connection', conn)
    sel.register(conn, selectors.EVENT_READ, recv)


def close(sock): 
    sel.unregister(sock)
    sock.close()

def recv(sock):
    print("receiving from socket")
    packet = packets.unpack(sock.recv(MAX_READ))
    print("packet is: ", packet)
    if not packet:
        print('Read empty packet, closing connection', sock)
        close(sock)
        return
    if packet['opcode'] == OP_GETATTR:
        print('Received OP_GETATTR in node.py')
        reply = packets.new_packet(OP_GETATTR_R)
        reply['getattr'] = filesystem.getattr(packet['path']) # call getattr locally
        print('Sending OP_GETATTR_R', reply)
        sock.send(packets.build(reply))

    elif packet['opcode'] == OP_BYE_R:
        close(sock)
        os.kill(os.getpid(),signal.SIGKILL)
        sys.exit(0)
 
    elif packet['opcode'] == OP_READ:
        print("Received OP_READ in node.py")
        reply = packets.new_packet(OP_READ_R)
        reply['read'] = filesystem.read(packet['path'],packet['size'],packet['offset'],packet['fh']).decode()
        print('Sending OP_READ_R with ', reply['read'])
        sock.send(packets.build(reply))

    elif packet['opcode'] == OP_WRITE:
        print("Received OP_WRITE in node.py")
        reply = packets.new_packet(OP_WRITE_R)
        reply['datalen'] = filesystem.write(packet['path'],packet['data'].encode(),packet['offset'],packet['fh'])
        print('Sending OP_WRITE_R with ', reply['datalen'])
        sock.send(packets.build(reply))

    elif packet['opcode'] == OP_TRUNC:
        print("Received OP_TRUNC in node.py")
        reply = packets.new_packet(OP_TRUNC_R)
        reply['trunc'] = filesystem.truncate(packet['path'],packet['length'])
        print('Sending OP_TRUNC_R with', reply['trunc'])
        sock.send(packets.build(reply))

    elif packet['opcode'] == OP_GETXATTR:
        print("Received OP_GETXATTR in nodde.py")
        reply = packets.new_packet(OP_GETXATTR_R)
        reply['getxattr'] = filesystem.getxattr(packet['path'],packet['name'])
        print('Sending OP_GETXATTR_R with', reply['getxattr'])
        sock.send(packets.build(reply))

    elif packet['opcode'] == OP_LEAVE:
        print("Bootstrap has exited, so we will exit too.")
        os.kill(os.getpid(),signal.SIGKILL)
        sys.exit(0)

    elif packet['opcode'] == OP_RENAME:
        print("Received OP_RENAME in node.py")
        reply = packets.new_packet(OP_RENAME_R)
        reply['rename'] = filesystem.rename(packet['old'],packet['new'])
        print("Sending OP_RENAME_R in node.py")
        sock.send(packets.build(reply))

    elif packet['opcode'] == OP_DELETE:
        print("Received OP_DELETE in node.py")
        reply = packets.new_packet(OP_DELETE_R)
        reply['delete'] = filesystem.unlink(packet['path'])
        print("Sending OP_DELETE_R in node.py")
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

def sigint_handler(signal2,frame):
    print("SIGINT~~~~~~~~~~~~~~")
    leave()
    #LEAVE HERE???
    os.kill(os.getpid(),signal.SIGKILL)
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT,sigint_handler)
    setup_args()
    print(args)
    if args.ip:
        bootstrap_ip = args.ip
    print("Starting FUSE...")
    #logging.basicConfig(level=logging.DEBUG)
    if not os.path.exists(args.mount):
        try:
            os.makedirs(args.mount)
        except:
            print("\033[91m"+"Directory " + args.mount + " is already mounted. Please unmount and try again.")
            print("To unmount, maybe try \033[1m $fusermount -uz " + args.mount)
            sys.exit(0)
    intro()
    join()
    t = threading.Thread(target=fuse_thread, name='fuse_thread')
    t.setDaemon(True)
    t.start()
    sel.register(sys.stdin, selectors.EVENT_READ, do_cmd)
    sel.register(listen_sock, selectors.EVENT_READ, accept)
    while True:
            prompt()
            events = sel.select()
            for key, mask in events: # dw about mask
                    print(key)
                    callback = key.data
                    callback(key.fileobj)
