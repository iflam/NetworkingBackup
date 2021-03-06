import socket
import sys
import threading
import selectors
MAXBYTES = 1
MOTD = "Wazzup yoooooo"
namedict = {} #Dict with name as key
sockdict = {} #Dict with socket as key
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
loc = "0.0.0.0"
verbose = False
HELP = "help:\n/help\t\tprints help menu\n/users\t\tprint list of users\n/shutdown\tshut down server"
lock = threading.Lock()
finish = False

def addUser(name,clientsocket):
    ##MUTEX HERE##
    with lock:
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
    with lock:
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
        if verbose: print("The name is:",cmd[1].replace(b"\r\n\r\n",b"").decode())
        e = addUser(cmd[1].replace(b"\r\n\r\n",b"").decode(),clientsocket)
        if(e == -1):
            clientsocket.send(b"ETAKEN\r\n\r\n")
        else:
            if verbose: print("New user!")
            clientsocket.send(b"MAI\r\n\r\n")
            clientsocket.send(f"MOTD {MOTD}\r\n\r\n".encode())
    else:
        print("idk what happens in this case -- NON-IAM")

def thread_function(clientsocket,buf): 
    ###REMEMBER: CLIENTSOCKET IS THE SOCKET THIS THREAD READS FROM, IT NEVER CHANGES###
    doLogin(clientsocket, buf)
    #Listen on info from my clientsocket
    while(not finish):
        buf = b""
        while not buf.endswith(b"\r\n\r\n"):
            buf+= clientsocket.recv(MAXBYTES)
        print("read buf")
        print(buf)

        ## Do Stuff based on what received.
        t = buf.split(b" ")
        cmd = t[0].replace(b"\r\n\r\n",b"")
        print("t")
        print(t)
        print(cmd)
        if cmd == b"TO":
            if verbose: print("cmd is TO")
            name = t[1].replace(b"\r\n\r\n",b"").decode()
            print("name", name)
            print(sockdict[clientsocket])
            if(name == sockdict[clientsocket]):
                if verbose: print("TO to self")
                clientsocket.send(f"EDNE {name}\r\n\r\n".encode())
                if verbose: print(f"Sent EDNE to {name}")
                continue;
            elif name in namedict:
                t[2:] = [ word.decode() for word in t[2:] ]
                msg = " ".join(t[2:])
                msg = msg.replace("\r\n\r\n", "")
                if verbose: print("msg", msg) 
                myname = sockdict[clientsocket]
                if verbose: print("sending FROM", myname, msg)
                sendString = f"FROM {myname} {msg}".encode() #TODO: Something here is going wrong. Might be from client though.
                if verbose: print("sendString", sendString)
                sendLoc = namedict[name]
                sendLoc.send(sendString)
            else:
                clientsocket.send(f"EDNE {name}\r\n\r\n".encode())
                if verbose: print("sent EDNE")
        elif cmd == b"LISTU":
            if verbose: print("Sending UTSIL")
            sendString = b"UTSIL " 
            for n in namedict:
                sendString += f"{n} ".encode()
            sendString+=b"\r\n\r\n"
            clientsocket.send(sendString)
            if verbose: print("Sent UTSIL")
        elif cmd == b"MORF":
            if verbose: print("is MORF")
            name = t[1].replace(b"\r\n\r\n",b"").decode()
            myname = sockdict[clientsocket]
            sendLoc = namedict[name]
            sendLoc.send(f"OT {myname}\r\n\r\n".encode())
            if verbose: print(f"sent OT {myname}\r\n\r\n")
        elif cmd == b"BYE":
            if verbose: print("Goodbye")
            name = removeUser(clientsocket)
            clientsocket.send(b"EYB\r\n\r\n")
            for x in sockdict:
                x.send(f"UOFF {name}\r\n\r\n".encode())
                #exit(0)
                return finish
        else:
            print("Garbage command. Exiting")
            exit(-1)
    return finish 

def accept():
    (clientsocket, address) = serversocket.accept()
    buf = b""
    while not buf.endswith(b"\r\n\r\n"):
        buf += clientsocket.recv(MAXBYTES)
        if verbose: print("buf loop, read", buf)

    ## Each individual thread will do this with their client:
    threading.Thread(target=thread_function,args=(clientsocket,buf),daemon=True).start()

def readIn():
    read_stdin = sys.stdin.readline()
    if verbose: print("read from selector", read_stdin)
    if read_stdin == "/users\n":
        print("users:")
        for n in namedict:
            print(n)
    elif read_stdin == "/help\n":
        print(HELP)
    elif read_stdin == "/shutdown\n":
        shutdown()

def shutdown():
    finish = True
    for th in threading.enumerate():
        if th != threading.current_thread():
            th.join(timeout=1) # wait for child threads to finish
    for sock in sockdict:
        print("closing", sock)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    print("closing serversocket")
    serversocket.shutdown(socket.SHUT_RDWR)
    serversocket.close()
    print("exiting")
    exit()

if __name__ == '__main__':
    print(sys.argv)
    if(sys.argv[1] == "-h"):
        print(HELP)
        exit(0)
    elif(sys.argv[1] == "-v"):
        verbose = True
        try:
        	numWorkers = int(sys.argv[3])
        except:
        	print("numWorkers must be an integer.")
        	exit(-1)
        serversocket.bind((loc,int(sys.argv[2])))
        serversocket.listen(numWorkers)
        MOTD = sys.argv[4]
    else:
        try:
        	numWorkers = int(sys.argv[2])
        except:
        	print("numWorkers must be an integer.")
        	exit(-1)
        serversocket.bind((loc,int(sys.argv[1])))
        serversocket.listen(numWorkers)
        MOTD = sys.argv[3]

    # prepare select to read stdin or socket accept
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ, readIn)
    sel.register(serversocket, selectors.EVENT_READ, accept)

    while True:
        events = sel.select(1)
        for key, mask in events:
            callback = key.data
            callback()
