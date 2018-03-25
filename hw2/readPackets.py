from structs import Ethernet

MAX_PACKET_LEN = 100

# read a full packet and build ethernet Struct
def readPacket(sock):
    packet = sock.recv(MAX_PACKET_LEN)
    return packet

# protocol is of type Struct (i.e. something we define in structs.py)
def printPacket(packet, protocol):
    parsed_packet = protocol.parse(packet)
    if protocol == Ethernet:
        print('mac_src', parsed_packet['mac_src'].hex())
        print('mac_dest', parsed_packet['mac_dest'].hex())
    elif protocol == IP:
        pass # print IP fields
    elif protocol == ARP:
        pass # print ARP fields
    elif protocol == DNS:
        pass # print DNS fields
    elif protocol == ICMP:
        pass # print ICMP fields

# TODO 
def stripEthernet(packet):
    return packet

# TODO: 
# identify protocol based on packet header
# note that packet contains the ethernet frame first, as currently implemented
# you can either change this outside this function (remove the ethernet frame from the packet before calling identifyProtocol) or simply skip over the ethernet frame here
def identifyProtocol(packet):
    pass

def hexdump(packet):
    print(packet) # prints as bytes object (for debugging, later remove)
    print(packet.hex()) # prints as hex
    # TODO: maybe check out that hexdump library to pretty print hex
