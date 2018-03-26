from construct import Struct, Bytes

ICMP = Struct(

	)

TCP = Struct(

	)

UDP = Struct(

	)

def protocolType(protocol):
	if protocol == 1:
		print("I am ICMP")
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
	data = protocolType(IP['protocol'].hex()) #TODO: GET THIS LINE WORKING
	)

Ethernet = Struct(
        'mac_dest' / Bytes(6),
        'mac_src' / Bytes(6),
        'type' / Bytes(2),
        ip = IP
        )

