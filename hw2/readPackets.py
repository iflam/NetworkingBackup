from structs import Ethernet, IP, TCP, UDP, ICMP, DNS, TYPE_STR, IP_TYPE, SBH, IDB
import time
MAX_PACKET_LEN = 100

# read a full packet and build ethernet Struct
def readPacket(sock):
    packet = sock.recv(MAX_PACKET_LEN)
    return packet

# protocol is of type Struct (i.e. something we define in structs.py)
def printPacket(parsed_packet, protocol):
    result = TYPE_STR[protocol] + '('
    result += printFields(parsed_packet) + ')'
    print(result)

def printFields(parsed_packet):
    result = ''
    for key in parsed_packet.keys():
        try:
            result += str(key) + '=' + str(parsed_packet[key].hex()) + ', '
            #print(key, ':', parsed_packet[key].hex())
        except: # hacky try/except -> hex() only works on Bytes fields, so if it doesn't we're dealing with BitsIntegers
            result += str(key) + '=' + str(parsed_packet[key]) + ', '
            #print(key, ':', parsed_packet[key])
    return result

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

def getSbHeader(f): #Length is passed as integer
    # 'blockType' = Bytes(4),
    # 'blockTLength' = Bytes(4),
    # 'byteOrderMagic' = Bytes(4),
    # 'major' = Bytes(2),
    # 'minor' = Bytes(2),
    # 'sec_len' = Bytes(4),
    # 'options' = Bytes(0),
    # 'blocktLength2' = Bytes(4)

    #hardcoded values:

    sb = {}
    sb['blockType'] = 0x0A0D0D0A
    sb['blockTLength'] = 28
    sb['byteOrderMagic'] = 0x1A2B3C4D
    sb['major'] = 1
    sb['minor'] = 0
    sb['sec_len'] = -1 
    sb['blockTLength2'] = 28
    f.write(SBH.build(sb))

def getIdBlock(f): #blocktype, linktype passed as saved in struct
    # 'blockType' = Bytes(4),
    # 'blockTLength' = Bytes(4),
    # 'linkType' = Bytes(2),
    # 'res' = Bytes(2),
    # 'snapLen' = Bytes(4),
    # 'options' = Bytes(0),
    # 'blockTLength2' = Bytes(4)

    #hardcoded values

    idb = {}
    idb['blockType'] =  0x00000001
    idb['blockTLength'] = 20
    idb['linkType'] = 1
    idb['res'] = 0
    idb['snapLen'] = MAX_PACKET_LEN 
    idb['blockTLength2'] = 20
    f.write(IDB.build(idb))


def getEpBlock(data): #pass as array
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
    dataLen = len(data)
    padAmt = 4-len(data)%4 if len(data) % 4 else 0
    data += (b"\x00"*padAmt)
    epb = {}
    epb['blockType'] = (6).to_bytes(4,byteorder='big')
    epb['blockTLength'] = (32+len(data)).to_bytes(4,byteorder='big')
    epb['interfaceID'] = b"\x00\x00\x00\x00"
    epb['timestamp'] = int(round(time.time()*1000000)).to_bytes(8,byteorder='big')
    epb['capturedp_len'] = dataLen.to_bytes(4,byteorder='big')
    epb['origp_len'] = dataLen.to_bytes(4,byteorder='big')
    epb['data'] = data
    epb['blockTLength2'] = (32+len(data)).to_bytes(4,byteorder='big')
    s = b""
    for x in epb:
        s+=epb[x]
    return s
