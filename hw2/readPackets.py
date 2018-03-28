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

def printpcap(outfile, packet, ip_type):
    test = ["1","2","3","4","5","6","7","8","9"]
    printSbHeader(test)
    printIdBlock(test)
    printEpBlock(test)


def printSbHeader(fields):
    breakLine ="   +"+"-"*63+"+"
    breakLine2 ="   +"+"-+"*32
    print("   0                   1                   2                   3")
    print("   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1")
    print(breakLine)
    a,b = 1,2
    print(' 0 | {0:^62}|'.format("Block Type = " + fields[0]))
    print(breakLine)
    print(' 4 | {0:^62}|'.format("Block Total Length = " + fields[1]))
    print(breakLine2)
    print(' 8 | {0:^62}|'.format("Byte-Order Magic = " + fields[2]))
    print(breakLine2)
    print('12 |{0:^31}|{0:^31}|'.format(fields[3],fields[4]))
    print(breakLine2)
    print('16 |'+' '*63+'|')
    print('   |{0:^63}|'.format("Section Length = " + fields[5]))
    print('   |'+' '*63+'|')
    print(breakLine2)
    print('24 /'+' '*63+'/')
    print('   /{0:^63}/'.format("Options (variable) = " + fields[6]))
    print('   /'+' '*63+'/')
    print(breakLine2)
    print('   | {0:^62}|'.format("Block Total Length = " + fields[7]))
    print(breakLine)

def printIdBlock(fields):
    breakLine ="   +"+"-"*63+"+"
    breakLine2 ="   +"+"-+"*32

    print("   0                   1                   2                   3")
    print("   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1")
    print(breakLine)
    a,b = 1,2
    print(' 0 | {0:^62}|'.format("Block Type = " + fields[0]))
    print(breakLine)
    print(' 4 | {0:^62}|'.format("Byte-Order Magic = " + fields[1]))
    print(breakLine2)
    print(' 8 |{0:^31}|{0:^31}|'.format(fields[2],fields[3]))
    print(breakLine2)
    print('12 |{0:^63}|'.format("SpanLen = " + fields[4]))
    print(breakLine2)
    print('16 /'+' '*63+'/')
    print('   /{0:^63}/'.format("Options (variable) = " + fields[5]))
    print('   /'+' '*63+'/')
    print(breakLine2)
    print('   | {0:^62}|'.format("Block Total Length = " + fields[6]))
    print(breakLine)

def printEpBlock(fields):
    breakLine ="   +"+"-"*63+"+"
    breakLine2 ="   +"+"-+"*32

    print("   0                   1                   2                   3")
    print("   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1")
    print(breakLine)
    a,b = 1,2
    print(' 0 | {0:^62}|'.format("Block Type = " + fields[0]))
    print(breakLine)
    ##

    print(' 4 | {0:^62}|'.format("Block Total Length = " + fields[0]))
    print(breakLine2)
    print(' 8 | {0:^62}|'.format("Interface ID = " + fields[1]))
    print(breakLine2)
    print('12 | {0:^62}|'.format("Timestamp (High) = " + fields[2]))
    print(breakLine2)
    print('16 | {0:^62}|'.format("Timestamp (Low) = " + fields[3]))
    print(breakLine2)
    print('20 | {0:^62}|'.format("Captured Packet Length = " + fields[4]))
    print(breakLine2)
    print('24 | {0:^62}|'.format("Original Packet Length = " + fields[5]))
    print(breakLine2)
    print('28 /'+' '*63+'/')
    print('   /{0:^63}/'.format("Packet Data = " + fields[6]))
    print('   /'+' '*63+'/')
    ##
    print(breakLine2)
    print('32 /'+' '*63+'/')
    print('   /{0:^63}/'.format("Options (variable) = " + fields[7]))
    print('   /'+' '*63+'/')
    print(breakLine2)
    print('   | {0:^62}|'.format("Block Total Length = " + fields[8]))
    print(breakLine)


