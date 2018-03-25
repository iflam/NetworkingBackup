import argparse
import socket
from structs import Ethernet
from readPackets import readPacket, stripEthernet, identifyProtocol, printPacket, hexdump

ETH_P_ALL = 3 # use to listen on promiscuous mode

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

    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL)) as sock:
        sock.bind((INTERFACE, 0))

        # main loop 
        while True: 
            packet = readPacket(sock) 
            if args_dict['hexdump']:
                hexdump(packet)
            if not args_dict['filter'] or args_dict['filter'] == 'Ethernet':
                printPacket(packet, Ethernet) # all packets have Ethernet on top
            packet = stripEthernet(packet) # now we are interested in the rest of the packet
            protocol = identifyProtocol(packet) 
            if not args_dict['filter'] or args_dict['filter'] == protocol:
                printPacket(packet, protocol)
            
