from structs import Ethernet, IP, TCP, UDP, ICMP, DNS, TYPE_STR, IP_TYPE

MAX_PACKET_LEN = 100

# read a full packet and build ethernet Struct
def readPacket(sock):
    packet = sock.recv(MAX_PACKET_LEN)
    return packet

# protocol is of type Struct (i.e. something we define in structs.py)
def printPacket(parsed_packet, protocol):
    print(TYPE_STR[protocol])
    printFields(parsed_packet)

def printFields(parsed_packet):
    for key in parsed_packet.keys():
        try:
            print(key, ':', parsed_packet[key].hex())
        except: # hacky try/except -> hex() only works on Bytes fields, so if it doesn't we're dealing with BitsIntegers
            print(key, ':', parsed_packet[key])

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
