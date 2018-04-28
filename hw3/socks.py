import socket 

def listen_sock(): # create a listening socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1) 
    return sock

def tcp_sock(): # tcp socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock
