#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
import os

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from consts import *
from opcodes import *
import packets
import socks
import signal

import socket

if not hasattr(__builtins__, 'bytes'):
    bytes = str


class Memory(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    # def sigint_handler(signal,frame):
    #     print("MEMORY EXITING")
    #     sys.exit(0)

    def __init__(self, bootstrap=None, node=None):
        self.bootstrap = bootstrap
        self.node = node
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(
            st_mode=(S_IFDIR | 0o755),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2)

    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFREG | mode),
            st_nlink=1,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())
        self.data[path] = ""
        packet = packets.new_packet(OP_CREATE)
        packet['path'] = path
        packet['loc'] = self.node
        sock = socks.tcp_sock()
        sock.connect(self.bootstrap)
        print('Connected to bootstrap', sock)
        print('Sending packet', packet)
        print('Built packet', packets.build(packet))
        sock.send(packets.build(packet)) # send new file to bootstrap
        sock.close()
        # should we wait for ack here?
        self.fd += 1
        return self.fd

    def destroy():
        pass

    def getattr(self, path, fh=None):
        print("memory.py getattr called")
        if path not in self.files:
            packet = packets.new_packet(OP_FIND) # ask bootstrap - find location of file
            packet['path'] = path
            print('Sending OP_FIND for getattr', packet)
            sock = socks.tcp_sock()
            sock.connect(self.bootstrap)
            sock.send(packets.build(packet))
            reply = packets.unpack(sock.recv(MAX_READ))
            print('Received OP_FIND_Rfor getattr', reply)
            if 'loc' not in reply:
                raise FuseOSError(ENOENT)
            loc = tuple(reply['loc'])
            tcp_sock = socks.tcp_sock() 
            tcp_sock.connect(loc) # connect to other node
            packet = packets.new_packet(OP_GETATTR)
            packet['path'] = path
            print('Sending OP_GETATTR', packet)
            tcp_sock.send(packets.build(packet)) # send syscall 
            reply = packets.unpack(tcp_sock.recv(MAX_READ)) # TODO: listen for reply in select
            print('Received OP_GETATTR_R', reply)
            if reply['getattr']:
                return reply['getattr']
            else: raise FuseOSError(ENOENT)
        return self.files[path]

    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFDIR | mode),
            st_nlink=2,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        self.files['/']['st_nlink'] += 1

    def open(self, path, flags):
        #We will need this one
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        print("memory.py read called")
        if path not in self.files:
            packet = packets.new_packet(OP_FIND) # ask bootstrap - find location of file
            packet['path'] = path
            print('Sending OP_FIND for READ', packet)
            sock = socks.tcp_sock()
            sock.connect(self.bootstrap)
            sock.send(packets.build(packet))
            reply = packets.unpack(sock.recv(MAX_READ))
            print('Received OP_FIND_R for READ', reply)
            if 'loc' not in reply:
                raise FuseOSError(ENOENT)
            loc = tuple(reply['loc'])
            tcp_sock = socks.tcp_sock() 
            tcp_sock.connect(loc) # connect to other node
            packet = packets.new_packet(OP_READ)
            packet['path'] = path
            packet['size'] = size
            packet['offset'] = offset
            packet['fh'] = fh
            print('Sending OP_READ', packet)
            tcp_sock.send(packets.build(packet)) # send syscall 
            reply = packets.unpack(tcp_sock.recv(MAX_READ)) # TODO: listen for reply in select
            print('Received OP_READ_R', reply)
            if 'read' in reply:
                return reply['read'].encode('utf-8')
            else: raise FuseOSError(ENOENT)
        print("offset: ", offset)
        print("size: ", size)
        print("read contents:",self.data[path])
        datalen = len(self.data[path])
        print("datalen", datalen)
        end = datalen
        if datalen > size:
            end = size
        return self.data[path][offset:offset + end].encode('utf-8')

    def readdir(self, path, fh):
        #This is where LS happens
        #return ['.', '..'] + [x[1:] for x in self.files if x != '/']
        packet = packets.new_packet(OP_LS)
        sock = socks.tcp_sock()
        sock.connect(self.bootstrap)
        sock.send(packets.build(packet))
        ls = packets.unpack(sock.recv(MAX_READ))
        print('ls contents', ls['ls'])
        return ['.', '..'] + [x[1:] for x in ls['ls']]

    def readlink(self, path):
        return self.data[path]

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        print("In Rename")
        brename = packets.new_packet(OP_RENAME)
        brename['old'] = old
        brename['new'] = new
        if old not in self.files:
            packet = packets.new_packet(OP_FIND) # ask bootstrap - find location of file
            packet['path'] = old
            print('Sending OP_FIND for RENAME', packet)
            sock = socks.tcp_sock()
            sock.connect(self.bootstrap)
            sock.send(packets.build(packet))
            reply = packets.unpack(sock.recv(MAX_READ))
            print('Received OP_FIND_R for RENAME', reply)
            if 'loc' not in reply:
                raise FuseOSError(ENOENT)
            loc = tuple(reply['loc'])
            tcp_sock = socks.tcp_sock() 
            tcp_sock.connect(loc) # connect to other node
            packet = packets.new_packet(OP_RENAME)
            packet['old'] = old
            packet['new'] = new
            print('Sending OP_RENAME', packet)
            tcp_sock.send(packets.build(packet)) # send syscall 
            reply = packets.unpack(tcp_sock.recv(MAX_READ)) # TODO: listen for reply in select
            print('Received OP_RENAME_R', reply)
        else:
            self.data[new] = self.data[old]
            del self.data[old]
            self.files[new] = self.files.pop(old)
            boot_sock = socks.tcp_sock()
            boot_sock.connect(self.bootstrap)
            boot_sock.send(packets.build(brename))

    def rmdir(self, path):
        # with multiple level support, need to raise ENOTEMPTY if contains any files
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        self.files[target] = dict(
            st_mode=(S_IFLNK | 0o777),
            st_nlink=1,
            st_size=len(source))

        self.data[target] = source

    def truncate(self, path, length, fh=None):
        # make sure extending the file fills in zero bytes
        self.data[path] = self.data[path][:length].ljust(
            length, b'\x00'.decode())
        self.files[path]['st_size'] = length

    def unlink(self, path):
        print("In Unlink")
        brename = packets.new_packet(OP_DELETE)
        brename['path'] = path
        if path not in self.files:
            print("In other location")
            packet = packets.new_packet(OP_FIND) # ask bootstrap - find location of file
            packet['path'] = path
            print('Sending OP_FIND for DELETE', packet)
            sock = socks.tcp_sock()
            sock.connect(self.bootstrap)
            sock.send(packets.build(packet))
            reply = packets.unpack(sock.recv(MAX_READ))
            print('Received OP_FIND_R for DELETE', reply)
            if 'loc' not in reply:
                raise FuseOSError(ENOENT)
            loc = tuple(reply['loc'])
            tcp_sock = socks.tcp_sock() 
            tcp_sock.connect(loc) # connect to other node
            packet = packets.new_packet(OP_DELETE)
            packet['path'] = path
            print('Sending OP_DELETE', packet)
            tcp_sock.send(packets.build(packet)) # send syscall 
            reply = packets.unpack(tcp_sock.recv(MAX_READ)) # TODO: listen for reply in select
            print('Received OP_DELETE_R', reply)
        else:
            print("In self")
            del self.data[path]
            self.files.pop(path)
            boot_sock = socks.tcp_sock()
            boot_sock.connect(self.bootstrap)
            boot_sock.send(packets.build(brename))

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        #THIS IS WHERE WRITE HAPPENS
        print("WRITE in Memory")
        if path not in self.files:
            print('remote write')
            packet = packets.new_packet(OP_FIND) # ask bootstrap - find location of file
            packet['path'] = path
            print('Sending OP_FIND for WRITE', packet)
            sock = socks.tcp_sock()
            sock.connect(self.bootstrap)
            sock.send(packets.build(packet))
            reply = packets.unpack(sock.recv(MAX_READ))
            print('Received OP_FIND_R for WRITE', reply)
            if 'loc' not in reply:
                raise FuseOSError(ENOENT)
            loc = tuple(reply['loc'])
            tcp_sock = socks.tcp_sock() 
            tcp_sock.connect(loc) # connect to other node
            packet = packets.new_packet(OP_WRITE)
            packet['path'] = path
            packet['data'] = data
            packet['offset'] = offset
            packet['fh'] = fh
            print('Sending OP_WRITE', packet)
            tcp_sock.send(packets.build(packet)) # send syscall 
            reply = packets.unpack(tcp_sock.recv(MAX_READ)) # TODO: listen for reply in select
            print('Received OP_WRITE_R', reply)
            if 'datalen' in reply:
                return reply['datalen']
            else: raise FuseOSError(ENOENT)
        print("local write")
        print("current contents:", self.data[path])
        print("offset", offset)
        print("fh", fh)
        self.data[path] = self.data[path][:offset].ljust(offset, b'\x00'.decode())
        self.data[path] += data.decode()
        self.data[path] += self.data[path][offset + len(data):]
        # self.data[path] = (
        #     # make sure the data gets inserted at the right offset
        #    self.data[path][:offset].ljust(offset, '\x00'.encode('ascii'))
        #    + data.decode()
        #     # and only overwrites the bytes that data is replacing
        #    + self.data[path][offset + len(data):])
        self.files[path]['st_size'] = len(self.data[path])
        print("current contents:", self.data[path])
        return len(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    if not os.path.exists(args.mount):
        os.makedirs(args.mount)
    fuse = FUSE(Memory(), args.mount, foreground=True)
