from structs import Ethernet, IP, TCP, UDP, ICMP, DNS

MAX_PACKET_LEN = 100

# read a full packet and build ethernet Struct
def readPacket(sock):
    packet = sock.recv(MAX_PACKET_LEN)
    return packet

# protocol is of type Struct (i.e. something we define in structs.py)
def printPacket(parsed_packet, protocol):
    if protocol == Ethernet:
        print('mac_src', parsed_packet['mac_src'].hex())
        print('mac_dest', parsed_packet['mac_dest'].hex())
        print('type', parsed_packet['type'].hex())
    elif protocol == IP:
        print('version', parsed_packet['version_hl'].hex())
        print('length', parsed_packet['total_length'].hex())
        print('protocol',parsed_packet['protocol'].hex())
        print('destip',parsed_packet['dest_ip'].hex())
    elif protocol == DNS:
        pass # print DNS fields
    elif protocol == ICMP:
        pass # print ICMP fields
    elif protocol == TCP:
        print('src_port', parsed_packet['src_port'].hex())
        print('dest_port', parsed_packet['dest_port'].hex())
        print('sequence number', parsed_packet['sequence_number'].hex())
        print('ack_number', parsed_packet['ack_number'].hex())
        print('doff_res_ns', parsed_packet['doff_res_ns'].hex())
        print('flags', parsed_packet['flags'].hex())
        print('window_size', parsed_packet['window_size'].hex())
        print('checksum', parsed_packet['checksum'].hex())
        print('urg_ptr', parsed_packet['urg_ptr'].hex())

# TODO 
def stripEthernet(packet):
    return packet

#TODO
def stripHeader(packet, size):
    return packet[size:]

def hexdump(packet):
    print(packet) # prints as bytes object (for debugging, later remove)
    print(packet.hex()) # prints as hex
    # TODO: maybe check out that hexdump library to pretty print hex
