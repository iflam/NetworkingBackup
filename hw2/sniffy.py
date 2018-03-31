import argparse
import socket
import signal
import sys
from structs import Ethernet, ETHER_TYPE, IP, IP_TYPE, TYPE_STR, UDP, DNS,ICMP
from readPackets import readPacket, stripHeader, printPacket, hexdump, getSbHeader, getIdBlock, getEpBlock
import time
ETH_P_ALL = 3 # use to listen on promiscuous mode
epString = b""

def sig_handler(signal, frame):
    print("You pressed CTRL+C!")
    endSniff()

def endSniff(): 
    if args_dict['output'] is not None:
        file = open(args_dict['output'],"wb")
        getSbHeader(file)
        getIdBlock(file)
        file.write(epString)
    print("Exiting!")
    sys.exit(0)

# returns a Namespace object (https://docs.python.org/3/library/argparse.html#argparse.Namespace)
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='File name to output to')
    parser.add_argument('-t', '--timeout', help='Amount of time to capture for before quitting. If no time specified ^C must be sent to close program')
    parser.add_argument('-x', '--hexdump', help='Print hexdump to stdout', action='store_true') # action='store_true' basically means this flag doesn't take arguments (will be True if it appears, False else)
    parser.add_argument('-f', '--filter', help='Filter for one specific protocol', choices=['UDP','Ethernet','DNS','IP','TCP','ICMP'])

    parser.add_argument('INTERFACE', help='interface to listen for traffic on')

    return parser.parse_args() 

if __name__=='__main__':
    args = parse()
    args_dict = vars(args) # vars(args) turns Namespace into a regular dictionary
    print(args) 
    print(args_dict) 

    INTERFACE = args_dict['INTERFACE']
    signal.signal(signal.SIGINT,sig_handler)
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL)) as sock:
        sock.bind((INTERFACE, 0))
        start = time.time()
        # main loop 
        while True: 
            if args_dict['timeout']:
                if time.time() > start + int(args_dict['timeout']):
                    endSniff()
                #Receive Packet
            packet = readPacket(sock) 
            originalPacket = packet
            if args_dict['hexdump']:
                hexdump(packet)
            #parse Ethernet
            ethernet_packet = Ethernet.parse(packet)
            if not args_dict['filter'] or args_dict['filter'] == 'Ethernet':
                printPacket(ethernet_packet, Ethernet) # all packets have Ethernet on top
                epString += getEpBlock(packet)
            try:
                protocol = ETHER_TYPE[ethernet_packet['type']]
            except:
                continue
            packet = stripHeader(packet, Ethernet.sizeof()) # now we are interested in the rest of the packet
            
            #parse IP
            ip_packet = IP.parse(packet)
            if not args_dict['filter'] or args_dict['filter'] == 'IP':
                printPacket(ip_packet, IP)
                epString += getEpBlock(packet)
                #epString += getEpBlock(packet)
            packet = stripHeader(packet, IP.sizeof()) #now we are interested in the rest of the stuff

            #parse TCP/UDP/ICMP
            ip_type = IP_TYPE[ip_packet['protocol']]
            transport_packet = ip_type.parse(packet)
            if not args_dict['filter'] or args_dict['filter'] == TYPE_STR[ip_type]:
                printPacket(transport_packet, ip_type)
                epString += getEpBlock(packet)
                #printpcap("hi",packet,ip_type)
            packet = stripHeader(packet, ip_type.sizeof())

            #DNS
            if ip_type == UDP and (not args_dict['filter'] or args_dict['filter'] == 'DNS'):
                data_packet = DNS.parse(packet)
                printPacket(data_packet, DNS) # print DNS!
                #if transport_packet['dest_port'] == b"\x00\x35" or transport_packet['src_port'] == b"\x00\x35":
                #packet = stripHeader(packet,ip_type.sizeof())
                epString += getEpBlock(packet)

            #if not args_dict['filter'] or args_dict['filter'] == TYPE_STR[DNS]:
            #    epString+=getEpBlock(packet)

            #if not args_dict['filter'] or args_dict['filter'] == protocol:
            #    printPacket(packet, protocol)
            
