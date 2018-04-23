from cmd import *
from consts import *

import json
import selectors
import socket
import sys

# globals
nodes = [] 

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

def accept(sock):
	conn, addr = sock.accept()
	print("accepted connection, receiving...")
	packet = json.loads(conn.recv(MAX_READ).decode())
	print(packet)
	nodes.append(addr)

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
	intro()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(("127.0.0.1", 1234))
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
		
