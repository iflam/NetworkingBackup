from structs import Ethernet, IP, TCP, UDP, ICMP, DNS, TYPE_STR, IP_TYPE
import time
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


def printSbHeader(length): #Length is passed as integer
    # 'blockType' = Bytes(4),
    # 'blockTLength' = Bytes(4),
    # 'byteOrderMagic' = Bytes(4),
    # 'major' = Bytes(2),
    # 'minor' = Bytes(2),
    # 'sec_len' = Bytes(4),
    # 'options' = Bytes(0),
    # 'blocktLength2' = Bytes(4)
    sb = {}
    sb['blockType'] = b"\x0A\x0D\x0D\x0A"
    sb['blockTLength'] = b"\x00\x00\x00\x16"
    sb['byteOrderMagic'] = b"\x1a\x2b\x3c\x4d"
    sb['major'] = b"\x00\x01"
    sb['minor'] = b"\x00\x00"
    sb['sec_len'] = length.to_bytes(4,byteorder='big')
    sb['blockTLength2'] = b"\x00\x00\x00\x16"
    s = b""
    for x in sb:
        s+=sb[x]
    #return sb['blockType']+sb['blockTLength']+sb['byteOrderMagic']+sb['major']+sb['minor']+sb['sec_len']+sb['blockTLength2']
    return s

def printIdBlock(linktype): #blocktype, linktype passed as saved in struct
    # 'blockType' = Bytes(4),
    # 'blockTLength' = Bytes(4),
    # 'linkType' = Bytes(2),
    # 'res' = Bytes(2),
    # 'snapLen' = Bytes(4),
    # 'options' = Bytes(0),
    # 'blockTLength2' = Bytes(4)
    idb = {}
    idb['blockType'] =  b"\x00\x00\x00\x01"
    idb['blockTLength'] = b"\x00\x00\x00\x14"
    idb['linkType'] = linktype
    idb['res'] = b"\x00\x00"
    idb['snapLen'] = b"\x00\x00"
    idb['blockTLength2'] = b"\x00\x00\x00\x14"
    s = b""
    for x in idb:
        s+=idb[x]
    return s


def printEpBlock(data): #pass as array
    # 'blockType' = Bytes(4),
    # 'blockTLength' = Bytes(4),
    # 'interfaceID' = Bytes(4),
    # 'ts_high' = Bytes(4),
    # 'ts_low' = Bytes(4),
    # 'capturedp_len' = Bytes(4),
    # 'origp_len' = Bytes(4),
    # 'packet_data' = Bytes(this.capturedp_len)
    # 'options' = Bytes(0),
    # 'blockTLength2' = Bytes(4)
    data+= b"\0"*(len(data)%32)
    epb = {}
    epb['blockType'] = b"\x00\x00\x00\x01"
    epb['blockTLength'] = (32+len(data)).to_bytes(4,byteorder='big')
    epb['timestamp'] = str(time.time()).encode()
    epb['capturedp_len'] = len(data).to_bytes(4,byteorder='big')
    epb['origp_len'] = len(data).to_bytes(4,byteorder='big')
    epb['data'] = data
    epb['blockTLength2'] = (32+len(data)).to_bytes(4,byteorder='big')
    s = b""
    for x in epb:
        s+=epb[x]
    return s
