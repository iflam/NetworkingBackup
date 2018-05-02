import socket 

def listen_sock(): # create a listening socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostbyname(socket.gethostname()), 0))
    sock.listen(1) 
    return sock

def tcp_sock(): # tcp socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock
