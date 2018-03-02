import socket
import sys
import threading
MAXBYTES = 1
MOTD = "Wazzup yoooooo"
namedict = {} #Dict with name as key
sockdict = {} #Dict with socket as key
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
loc = sys.argv[1]

def addUser(name,clientsocket):
	##MUTEX HERE##
	if(name in namedict):
		print("Taken.")
		##CLOSE MUTEX##
		return -1
	else:
		namedict[name] = clientsocket
		sockdict[clientsocket] = name
		##CLOSE MUTEX##
		return 0

def removeUser(clientsocket):
	##MUTEX HERE##
	if clientsocket in sockdict:
		name = sockdict[clientsocket]
		del sockdict[clientsocket]
		del namedict[name]
		##CLOSE MUTEX##
		return name
	else:
		##CLOSE MUTEX##
		return None

def doLogin(clientsocket, buf):
	if(buf == b"ME2U\r\n\r\n"):
		clientsocket.send(b"U2EM\r\n\r\n")
	else:
		print("Junk. Closing")
		exit(-1)
	buf = b""
	while not buf.endswith(b"\r\n\r\n"):
		buf += clientsocket.recv(MAXBYTES)
	if(buf.startswith(b"IAM")):
		cmd = buf.split(b" ")
		print("The name is:",cmd[1].replace(b"\r\n\r\n",b"").decode())
		e = addUser(cmd[1].replace(b"\r\n\r\n",b"").decode(),clientsocket)
		if(e == -1):
			clientsocket.send(b"ETAKEN\r\n\r\n")
		else:
			print("New user!")
			clientsocket.send(b"MAI\r\n\r\n")
			clientsocket.send(f"MOTD {MOTD}\r\n\r\n".encode())
	else:
		print("idk what happens in this case -- NON-IAM")

def thread_function(clientsocket,buf):
	doLogin(clientsocket, buf)
	#Listen on info from my clientsocket
	while(True):
		buf = b""
		while not buf.endswith(b"\r\n\r\n"):
			buf+= clientsocket.recv(MAXBYTES)

		## Do Stuff based on what received.
		t = buf.split(b" ",1)
		cmd = t[0].replace(b"\r\n\r\n",b"")
		print(cmd)
		if cmd == b"TO":
			print("cmd is TO")
		elif cmd == b"LISTU":
			print("list of users:")
			sendString = b"UTSIL " 
			for n in namedict:
				sendString += f"{n} ".encode()
			sendString+=b"\r\n\r\n"
			clientsocket.send(sendString)
		elif cmd == b"MORF":
			print("is MORF")
		elif cmd == b"BYE":
			print("Goodbye")
			name = removeUser(clientsocket)
			clientsocket.send(b"EYB\r\n\r\n")
			for x in sockdict:
				x.send(f"UOFF {name}\r\n\r\n".encode())
				exit(0)
		else:
			print("Garbage command. Exiting")
			exit(-1)



if __name__ == '__main__':
	if loc != "localhost":
		int(loc)
	serversocket.bind((loc,int(sys.argv[2])))
	serversocket.listen(5)
	while True:
		(clientsocket, address) = serversocket.accept()
		buf = b""
		while not buf.endswith(b"\r\n\r\n"):
			buf += clientsocket.recv(MAXBYTES)

		## Each individual thread will do this with their client:
		threading.Thread(target=thread_function,args=(clientsocket,buf)).start()


