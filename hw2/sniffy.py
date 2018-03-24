import argparse
import socket
from structs import ethernet

MAX_PACKET_LEN = 100

def hexdump():
    print('hexdump')

# returns a Namespace object (https://docs.python.org/3/library/argparse.html#argparse.Namespace)
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='File name to output to')
    parser.add_argument('-t', '--timeout', help='Amount of time to capture for before quitting. If no time specified ^C must be sent to close program')
    parser.add_argument('-x', '--hexdump', help='Print hexdump to stdout', action='store_true') # action='store_true' basically means this flag doesn't take arguments (will be True if it appears, False else)
    parser.add_argument('-f', '--filter', help='Filter for one specific protocol', choices=['UDP','Ethernet','DNS','IP','TCP'])

    parser.add_argument('INTERFACE', help='interface to listen for traffic on')

    return parser.parse_args() 

if __name__=='__main__':
    args = parse()
    args_dict = vars(args) # vars(args) turns Namespace into a regular dictionary
    print(args) 
    print(args_dict) 

    INTERFACE = args_dict['INTERFACE']
    ETH_P_ALL = 3

    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL)) as sock:
        sock.bind((INTERFACE, 0))
        while True:
            packet = sock.recv(MAX_PACKET_LEN)
            print(packet)
            print(packet.hex())
            ethernet_packet = ethernet.parse(packet)
            print('mac_src', ethernet_packet['mac_src'].hex())
            print('mac_dest', ethernet_packet['mac_dest'].hex())

        # do things based on arguments here
        if args_dict['hexdump']: # you check args in the dict by name (default name is the long option i.e. hexdump, not the short option i.e. x, even if user used the short option)
            hexdump()

