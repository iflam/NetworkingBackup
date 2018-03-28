from construct import Struct, Bytes, BitStruct, Bit, BitsInteger, Octet, Bytewise

ICMP = Struct(
	'type' / Bytewise(Bytes(1)),
	'code' / Bytewise(Bytes(1)),
	'checksum' / Bytewise(Bytes(2)),
	'rest' / Bytewise(Bytes(4))
	)

TCP = BitStruct(
	'src_port' / Bytewise(Bytes(2)),
	'dest_port' / Bytewise(Bytes(2)),
	'sequence_number' / Bytewise(Bytes(4)),
	'ack_number' / Bytewise(Bytes(4)),
	#'doff_res_ns' / Bytewise(Bytes(1)), #4 bytes data offset, 3 bytes reserve, 1 byte NS
	'doff' / BitsInteger(4), #4 bytes data offset, 3 bytes reserve, 1 byte NS
	'res' / BitsInteger(3), #4 bytes data offset, 3 bytes reserve, 1 byte NS
	'ns' / BitsInteger(1), #4 bytes data offset, 3 bytes reserve, 1 byte NS
	'flags' / Bytewise(Bytes(1)),
	'window_size' / Bytewise(Bytes(2)),
	'checksum' / Bytewise(Bytes(2)),
	'urg_ptr' / Bytewise(Bytes(2))
	)

UDP = Struct(
        'src_port' / Bytes(2),
        'dest_port' / Bytes(2),
        'length' / Bytes(2),
        'checksum' / Bytes(2),

	)

DNS = BitStruct(
	 'identification' / Bytewise(Bytes(2)),
	 'qr' / BitsInteger(1),
	 'opcode' / BitsInteger(4),
	 'flags' / BitsInteger(7),
	 'rcode' / BitsInteger(4),
	 'total_questions' / Bytewise(Bytes(2)),
	 'total_answer' / Bytewise(Bytes(2)),
	 'total_authority' / Bytewise(Bytes(2)),
	 'total_additional' / Bytewise(Bytes(2)),
	)

# IP level protocols
def protocolType(protocol):
	if protocol == 1:
		return ICMP
	elif protocol == 6:
		return TCP
	elif protocol == 11:
		return UDP
	else:
		return None

IP = BitStruct(
	#word 1
	'version' / BitsInteger(4), #This is 4bits vers 4bits header length
	'hl' / BitsInteger(4), #This is 4bits vers 4bits header length
	'dscp' / Bytewise(Bytes(1)), #Differentiated Services
	'total_length' / Bytewise(Bytes(2)),
	#word 2
	'identification' / Bytewise(Bytes(2)),
	'flags' / BitsInteger(3), #3 bits for flags, 13 for fragment offset
	'fragoff' / BitsInteger(13), #3 bits for flags, 13 for fragment offset
	#word 3
	'time_to_live' / Bytewise(Bytes(1)),
	'protocol' / Bytewise(Bytes(1)),
	'checksum' / Bytewise(Bytes(2)), #header checksum
	#word 4
	'src_ip' / Bytewise(Bytes(4)),
	#word 5
	'dest_ip' / Bytewise(Bytes(4)),
	#If header length is greater than 5:
	#'options' / Bits(32)
	# data = protocolType(IP['protocol'].hex()) #TODO: GET THIS LINE WORKING
	)

Ethernet = Struct(
        'mac_dest' / Bytes(6),
        'mac_src' / Bytes(6),
        'type' / Bytes(2),
        # ip = IP
        )
ETHER_TYPE = { b'\x08\x00': IP}
DNS = "Bloop"	
IP_TYPE = {b'\x01': ICMP, b'\x06': TCP, b'\x11': UDP}
TYPE_STR = {ICMP:"ICMP",TCP:"TCP",UDP:"UDP",DNS:"DNS", Ethernet:"Ethernet", IP:"IP"}
