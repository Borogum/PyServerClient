# -*- coding: utf-8 -*-

# @Author: Darío M. García Carretero
# @Date:   2018-09-18T09:36:04+02:00
# @Email:  dario.aviles@gmail.com
# @Last modified by:   Darío M. García Carretero
# @Last modified time: 2018-09-18T09:36:04+02:00


import os
import configparser
import argparse
import socket
import sys
import struct
import time

class Client(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.encoding = 'utf8'
        self.max_bytes_len = 8
        self.max_bytes_str = '@Q'
        self.max_command_len = pow(2, self.max_bytes_len*8)

    def comunicate(self, s):
        li = len(s.encode(self.encoding))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        try: # This solve problem with versions 2.x and 3.x
            sock.send(struct.pack(self.max_bytes_str, li)+s)
        except TypeError:
            sock.send(li.to_bytes(self.max_bytes_len, sys.byteorder)+bytearray(s, self.encoding))

        l, = struct.unpack(self.max_bytes_str, sock.recv(self.max_bytes_len))
        total_received = 0
        m = ''
        while total_received<l:
            r = sock.recv(l).decode(self.encoding)
            m += r
            total_received += len(r)
        return m



if __name__ == '__main__':

    config = configparser.ConfigParser()
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('config', help='Config file')
    args = argument_parser.parse_args()
    config_path = os.path.realpath(args.config)
    config.readfp(open(config_path))
    host = config.get('general', 'host')
    port = config.getint('general', 'port')
    client = Client(host, port)
    try:
        s = 'HELLO'
        m = client.comunicate(s)
        print(m)
        while s.upper() not in ("EXIT", "QUIT") :
            print('>>', end=' ', flush=True )
            s = sys.stdin.readline().strip()
            li = len(s.encode(client.encoding))
            if li <= client.max_command_len:
                m = client.comunicate(s)
                print('<<', m)
            else:
                print('>>', 'Command to long')
            if s == quit:
                break
    except Exception as e:
        print('Uh oh!. Problems with connexion. Is server running?. '+
                    'Try control alt delete, '
                    'jiggle the cord, ' +
                    'turn server off and on, ' +
                    'clean the gunk out of the mouse or ' +
                    'call technical support.')
