I integrated memory.py with node.py - node.py simply creates an instance of Memory and calls fuse(Memory...) 

I changed our protocol a bit to resolve practical concerns regarding who holds sockets, how many, how long are they open, etc. 

The basic idea is no one maintains a permanent connection with anyone. Temporary connections are made for specific operations 
(e.g.
	import socks
	sock = socks.tcp_sock() # tcp_sock is a convenience method so you don't have to deal with socket.socket(AF_INET, SOCK_STREAM, etc.)
	sock.connect(some_addr)
	# do something
	sock.close() 
)
Of course, these temporary sockets need some_addr to connect to. Therefore, every node and the bootstrap are constantly listening for connections. node.py and bootstrap.py each have their own accept() function, in which they register select to receive packets from a new connection. Packets are then received in the recv() function. This is where packets are unpacked and a specific action is taken according to their opcode
(something like:
	def recv(sock):
		packets.unpack(sock.recv(MAX_READ))
		if packets['opcode'] == OP_A: # do the A thing
		elif packets['opcode'] == OP_B: # do the B thing
)
unpack is necessary because our packets are json but only raw bytes are sent through sockets. Likewise before you send a dict/json packet, you call packets.build(packet) 

Protocol:
Every packet must have an opcode. The rest is opcode dependent.
opcodes are consts defined in opcodes.py. Their names are all caps, and replies have the same name as the original with _R appended (e.g. the reply to OP_LS is OP_LS_R)

Examples:
See join() in node.py for example communication between node and bootstrap:
node creates temp_sock using socks.tcp_sock() 
node connects to bootstrap using temp_sock.connect((bootstrap_ip, args.port))
node builds packet using packets.new_packet() and sends it through temp_sock
The procedure for communicating with another node is:
node creates temp_sock
node connects to bootstrap (same as above)
node sends packets.new_packet(OP_FIND) with filename (packet['path'])
bootstrap replies with OP_FIND_R and location of other node (files[packet['path']].getpeername())
node receives reply, creates another temp_sock, connects to reply['loc'] and sends some syscall

Fuse:
memory.py has the following working:
create
getattr
readdir
Note that create and readdir involve communication only between a node and the bootstrap, while getattr involves a node asking the bootstrap for the location of a file, and then connecting to that node (assuming the file is not available locally). Once the node which called getattr initially connects to the node which owns the file, the node which owns the file runs getattr locally (by calling filesystem.gettatr()) and sends the result to the original caller

Testing:
Open up 4 terminals 
1. 
	bootstrap.py 
2. 
	node.py
3. 
	node.py -m mnt2
4. 
	touch mnt/hey
	touch mnt2/hey2
	ls mnt
	ls mnt2
You should see both files hey and hey2 in both mount directories

Arguments:
bootstrap.py and node.py take a port (-p) argument (specifying the port the bootstrap listens on, default=1234). Make sure you give node.py the same port as bootstrap.py
node.py takes a mount (-m) argument (default='mnt'). Make sure you give each node a different mount directory

Known issues:
Probably the most important thing atm is to just get enough syscalls working for echo and cat, maybe rm
Graceful exits - right now, you just have to CTRL+C everything. Your mount directories will probably not be reusable (device busy). You can unmount them with 'fusermount -uz mnt' so you don't have to reboot. 

Debugging:
bootstrap.py and node.py both have a nifty command line set up where you can type in the name of any global variable and it will print the value
(e.g.
	DiFUSE Bootstrap> nodes
	[Socket1, Socket2,...]
	DiFUSE Bootstrap> files
	{'/file1': Socket1, '/file2': Socket2,...}
)
