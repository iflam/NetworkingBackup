from construct import Struct, Bytes

ICMP = Struct(

	)

TCP = Struct(
	'src_port' / Bytes(2),
	'dest_port' / Bytes(2),
	'sequence_number' / Bytes(4),
	'ack_number' / Bytes(4),
	'doff_res_ns' / Bytes(1), #4 bytes data offset, 3 bytes reserve, 1 byte NS
	'flags' / Bytes(1),
	'window_size' / Bytes(2),
	'checksum' / Bytes(2),
	'urg_ptr' / Bytes(2)
	)

UDP = Struct(
        'src_port' / Bytes(2),
        'dest_port' / Bytes(2),
        'length' / Bytes(2),
        'checksum' / Bytes(2),

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

IP = Struct(
	#word 1
	'version_hl' / Bytes(1), #This is 4bits vers 4bits header length
	'dscp' / Bytes(1), #Differentiated Services
	'total_length' / Bytes(2),
	#word 2
	'identification' / Bytes(2),
	'flags_and_fragoff' / Bytes(2), #3 bits for flags, 13 for fragment offset
	#word 3
	'time_to_live' / Bytes(1),
	'protocol' / Bytes(1),
	'checksum' / Bytes(2), #header checksum
	#word 4
	'src_ip' / Bytes(4),
	#word 5
	'dest_ip' / Bytes(4),
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
