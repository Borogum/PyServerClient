# -*- coding: utf-8 -*-

# @Author: Darío M. García Carretero
# @Date:   2018-09-18T09:36:04+02:00
# @Email:  dario.aviles@gmail.com
# @Last modified by:   Darío M. García Carretero
# @Last modified time: 2018-09-18T14:41:03+02:00


import sys
import configparser
import argparse
import os
import threading
import socket
import time
import struct
import client


class Command(object):

    def __init__(self, m):
        self.m = m

    def run(self, server, clientsocket, *args, **kwargs):
        raise NotImplementedError()


class ReplyCommand(Command):

    def run(self, server, clientsocket, *args, **kwargs):

        try:
            li = len(self.m.encode(server.encoding))
            clientsocket.send(li.to_bytes(server.max_bytes_len, sys.byteorder)+bytearray(self.m, server.encoding))
            clientsocket.close()
        except ConnectionResetError: #Remote hosts disconnected
            pass


class QuitCommand(ReplyCommand):

    def __init__(self, m):
        super(QuitCommand, self).__init__('Shutting down server. Bye!')

class HelloCommand(ReplyCommand):

    def run(self, server, clientsocket, *args, **kwargs):
        self.m = 'Hi there!, wellcome to {0} at port {1}'.format(server.host, server.port)
        super(HelloCommand, self).run(server, clientsocket)

class ExitCommand(ReplyCommand):

    def run(self, server, clientsocket, *args, **kwargs):
        self.m = 'Thanks for the visit, come back soon!'
        super(ExitCommand, self).run(server, clientsocket)

class TestCommand(ReplyCommand):

    def run(self,server,clientsocket,*args,**kwargs):
        self.m = 'TESTING' #Return message
        super(TestCommand, self).run(server,clientsocket)

# PUT YOURS COMMANDS HERE!


class  Parser(object):

    def transform_command(self, command):
        return ''.join([x.capitalize() for x in command.split('_')])+'Command'

    def parse(self,s):
        thismodule = sys.modules[__name__]
        c = s.split()
        if len(c):
            command=ReplyCommand('Um? "%s". I don\'t know what you are talking about.' % s.strip())
            try:
                command=getattr(thismodule, self.transform_command(c[0]))(' '.join(c[1:]))
            except AttributeError:
                pass
        else:
            command=ReplyCommand('')
        return command


class Server(object):

    def __init__(self,host,port,**kwargs):

        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.encoding = 'utf8'
        self.max_bytes_len = 8
        self.max_bytes_str = '@Q'
        self.max_command_len = pow(2, self.max_bytes_len*8)


    def serve(self):

        parser = Parser()
        command = None
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind((host, port))
        serversocket.listen(5)
        while (type(command) is not QuitCommand):
            (clientsocket, address) = serversocket.accept()
            l, = struct.unpack(self.max_bytes_str, clientsocket.recv(self.max_bytes_len))
            m = clientsocket.recv(l).decode(self.encoding)
            command = parser.parse(m)
            threading.Thread(target=command.run, args=(self,clientsocket,), kwargs=self.kwargs).start()


if __name__ == '__main__':

    config = configparser.ConfigParser()
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('config', help='Config file')
    args = argument_parser.parse_args()
    config_path = os.path.realpath(args.config)
    config.readfp(open(config_path))
    host = config.get('general','host')
    port = config.getint('general','port')
    server = Server(host,port)
    st = threading.Thread(target=server.serve)
    st.start()
    print('Started server at "{0}" in port "{1}". '.format(host,port),end='')
    print('Close this window or use "CTR+C" to stop server  ',end='',flush=True)
    while st.isAlive():
        try:
            for cursor in '\\|/-':
              time.sleep(0.5)
              sys.stdout.write('\b{}'.format(cursor))
              sys.stdout.flush()
        except KeyboardInterrupt:
            client.Client(host,port).comunicate('QUIT')
            print('\nSignal received finishing pending tasks', end='')
    print('\nServer stopped', flush=True)
