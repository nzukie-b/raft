#!/usr/bin/env python3
import argparse, socket, ssl, re
from os import name
from collections import namedtuple
from enum import Enum
from typing import Tuple
from constants import *
from utilities import *

parser = argparse.ArgumentParser()
parser.add_argument('operation', action='store', type=str, 
    help='The operation to execute. Valid operations are ls, rm, rmdir, mkdir, cp, and mv') 
parser.add_argument('params', action='store', nargs='+', 
    help='Parameters for the given operation. Will be one or two paths and/or URLs.')

def get_socket(host, port, timeout=30) -> socket.SocketType:
    sock = socket.create_connection((host, port), timeout=timeout)
    return sock

def encrypt_socket(socket: socket.SocketType, host) -> socket.SocketType:
    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(socket, server_hostname=host)
    return wrapped_socket

def __recv_msg(sock: socket.SocketType):
    data = sock.recv(8192)
    return data

def recv_full_msg(socket: socket.SocketType):
    msgText = __recv_msg(socket).decode('utf-8')
    # Read until new line
    while msgText.count('\r\n') == 0:
        msgText += __recv_msg(socket)
    return msgText

def parse_ftp_url(url: str) ->  dict:
    user = USERNAME
    pword = PASSWORD
    port = DEFAULT_PORT
    paths = []
    if url.startswith('ftps://'):
        url = re.split('ftps://', url)[1]
    else:
        print('Invalid ftps url')
        return
    if '@' in url:
        url_info = re.split('@', url)
        login_info = url_info[0]
        if ':' in login_info:
            login_info = re.split(':', login_info)
            user = login_info[0]
            pword = login_info[1]
        else:
            user = login_info
        url = url_info[1]
    temp = url.split('/', 1)
    host = temp[0]
    if ':' in host:
        host_info = re.split(':', url)
        host = host_info[0]
        port = host_info[1]
    if len(temp) > 1:
        paths = temp[1].split()
    else:
        paths.append('/')
    print('username: {}, password: {}, host: {}, port: {}, paths: {}'.format(user, pword, host, port, paths))
    ftp_url_info = {
        USER : user,
        PASS: pword,
        HOST: host,
        PORT: int(port),
        PATHS: paths
    }
    return ftp_url_info

def handle_login(socket: socket.SocketType, username, password):
    send_username(socket, username)
    print(recv_full_msg(socket))
    send_password(socket, password)
    print(recv_full_msg(socket))


def parse_data_channel(msg):
    """Parses the response from the PASV command. Returns a tuple of (ip_address, port_number)"""
    # TODO: CODE = 200? 
    #format: 227 Entering Passive Mode (192,168,150,90,195,149).
    channel_values = [int(a) for a in msg[msg.index('(') + 1: -2].split(',')]
    ip_addr = '{}.{}.{}.{}'.format(*channel_values)
    port = (channel_values[4] << 8) + channel_values[5]
    return (ip_addr, port)



def run_loop():
    while True:
        command = input('./c3700ftp ')
        params = command.split()
        print(params)
        op = OPERATIONS_DICT.get(params[0])
        #TODO: Determine 
        if op:
            print(op)
            break

        
def main(args):
    #TODO: Need to parse args firts to get host and port
    ftp_info = parse_ftp_url(args.params[0])
    if not ftp_info:
        return
    socket = get_socket(ftp_info.get(HOST), ftp_info.get(PORT))
    send_auth(socket)
    print(recv_full_msg(socket))
    socket = encrypt_socket(socket, ftp_info.get(HOST))
    print(args)
    handle_login(socket, ftp_info[USER], ftp_info[PASS])
    set_prot_buffer(socket)
    print(recv_full_msg(socket))
    set_prot_level(socket)
    print(recv_full_msg(socket))
    set_conn_type(socket)
    print(recv_full_msg(socket))
    set_conn_mode(socket)
    print(recv_full_msg(socket))
    set_conn_file(socket)
    print(recv_full_msg(socket))
    send_quit(socket)
    print(recv_full_msg(socket))
    socket.close()
    # run_loop()

    
if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    main(args)






