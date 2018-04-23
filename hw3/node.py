from cmd import *
from consts import *
from opcodes import *

import argparse
import json
import selectors
import socket
import sys

bootstrap_ip = "127.0.0.1" 
bootstrap_port = 1234 
bootstrap_sock = None
tier = "basic"
args = None

def intro():
	print("***DiFUSE Client***")
	print("Connected to bootstrap " + bootstrap_ip + " port " + str(bootstrap_port))
	print("Type help for a list of commands")

def setup_args():
	global args
	parser = argparse.ArgumentParser()
	parser.add_argument("-ip", help="ip of bootstrap")
	parser.add_argument("-p", "--port", help="port of bootstrap")
	parser.add_argument("-t", "--tier", choices=["basic", "hash", "repl"], help="DiFUSE hw tier")
	args = parser.parse_args()

def join():
	global bootstrap_sock
	bootstrap_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	bootstrap_sock.connect((bootstrap_ip, bootstrap_port))
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
	print("bootstrap_port\t print bootstrap port")

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
	intro()
	join()
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
