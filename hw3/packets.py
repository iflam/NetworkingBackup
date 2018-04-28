from opcodes import *

import json

def new_packet(opcode):
    return {'opcode': opcode}
def build(packet):
    packet = json.dumps(packet).encode()
    #if 'loc' in packet: packet['loc'] = tuple(packet['loc'])
    return packet
def unpack(packet):
    if not packet:
        return None
    return json.loads(packet.decode())

def join_packet(loc):
    packet = new_packet(OP_JOIN)
    packet['loc'] = loc
    return packet
