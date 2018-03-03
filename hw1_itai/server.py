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
loc = sys.argv[1]
HELP = "help:\n/help\t\tprints help menu\n/users\t\tprint list of users\n/shutdown\tshut down server"

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
    ###REMEMBER: CLIENTSOCKET IS THE SOCKET THIS THREAD READS FROM, IT NEVER CHANGES###
    doLogin(clientsocket, buf)
    #Listen on info from my clientsocket
    while(True):
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
            print("cmd is TO")
            name = t[1].replace(b"\r\n\r\n",b"").decode()
            print("name", name)
            if name in namedict:
                t[2:] = [ word.decode() for word in t[2:] ]
                msg = " ".join(t[2:])
                msg = msg.replace("\r\n\r\n", "")
                print("msg", msg) 
                myname = sockdict[clientsocket]
                print("sending FROM", myname, msg)
                sendString = f"FROM {myname} {msg}".encode() #TODO: Something here is going wrong. Might be from client though.
                print("sendString", sendString)
                sendLoc = namedict[name]
                sendLoc.send(sendString)
            else:
                clientsocket.send(f"EDNE {name}\r\n\r\n".encode())
                print("sent EDNE")
        elif cmd == b"LISTU":
            sendString = b"UTSIL " 
            for n in namedict:
                sendString += f"{n} ".encode()
            sendString+=b"\r\n\r\n"
            clientsocket.send(sendString)
        elif cmd == b"MORF":
            print("is MORF")
            name = t[1].replace(b"\r\n\r\n",b"").decode()
            myname = sockdict[clientsocket]
            sendLoc = namedict[name]
            sendLoc.send(f"OT {myname}\r\n\r\n".encode())
            print(f"sent OT {myname}\r\n\r\n")
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


def accept():
    (clientsocket, address) = serversocket.accept()
    buf = b""
    while not buf.endswith(b"\r\n\r\n"):
        buf += clientsocket.recv(MAXBYTES)
        print("buf loop, read", buf)

    ## Each individual thread will do this with their client:
    threading.Thread(target=thread_function,args=(clientsocket,buf),daemon=True).start()

def readIn():
    read_stdin = sys.stdin.readline()
    print("read from selector", read_stdin)
    if read_stdin == "/users\n":
        print("users:")
        for n in namedict:
            print(n)
    elif read_stdin == "/help\n":
        print(HELP)
    elif read_stdin == "/shutdown\n":
        shutdown()

def shutdown():
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
    if loc != "localhost":
        int(loc)
    serversocket.bind((loc,int(sys.argv[2])))
    serversocket.listen(5)

    # prepare select to read stdin or socket accept
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ, readIn)
    sel.register(serversocket, selectors.EVENT_READ, accept)

    while True:
        events = sel.select(1)
        for key, mask in events:
            callback = key.data
            callback()
