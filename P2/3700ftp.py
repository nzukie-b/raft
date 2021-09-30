#!/usr/bin/env python3
import argparse, socket, ssl, re, os
from io import FileIO
from os import name
from typing import BinaryIO
from enum import Enum
from typing import Any, Callable, Tuple
from constants import *
from utilities import *

parser = argparse.ArgumentParser()
parser.add_argument('operation', action='store', type=str, 
    help='The operation to execute. Valid operations are ls, rm, rmdir, mkdir, cp, and mv') 
parser.add_argument('params', action='store', nargs='+', 
    help='Parameters for the given operation. Will be one or two paths and/or URLs.')

def get_socket(address: tuple, timeout=30) -> socket.SocketType:
    sock = socket.create_connection(address, timeout=timeout)
    return sock

def encrypt_socket(socket: socket.SocketType, host) -> socket.SocketType:
    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(socket, server_hostname=host)
    return wrapped_socket

def __recv_data(sock: socket.SocketType):
    data = sock.recv(8192)
    return data

def recv_full_msg(socket: socket.SocketType):
    msgText = __recv_data(socket).decode('utf-8')
    # Read until end of response
    while msgText.count('\r\n') == 0:
        msgText += __recv_data(socket)
    return msgText

def parse_ftp_url(params: list) ->  dict:
    user = USERNAME
    pword = PASSWORD
    port = DEFAULT_PORT
    remote_path = None
    local_path = ''
    for path in params:
        if path.startswith('ftps://'):
            is_local = False
            path = re.split('ftps://', path)[1]
        else:
            is_local = True

        if is_local:
            local_path = os.path.join(os.getcwd(), path)
        elif '@' in path:
            url_info = re.split('@', path)
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
            remote_path = '/'+temp[1] if temp[1] else '/'
            # TODO: append / to the remote path actually needed?
    print('username: {}, password: {}, host: {}, port: {}, remote_path: {}, local_path: {}'.format(user, pword, host, port, remote_path, local_path))
    ftp_url_info = {
        USER : user,
        PASS: pword,
        HOST: host,
        PORT: int(port),
        REMOTE: remote_path,
        LOCAL: local_path,
    }
    return ftp_url_info

def handle_login(socket: socket.SocketType, host:str , username:str, password: str) -> socket.SocketType:
    send_auth(socket)
    get_response(socket)
    socket = encrypt_socket(socket, host)
    send_username(socket, username)
    get_response(socket)
    send_password(socket, password)
    get_response(socket)
    set_prot_buffer(socket)
    get_response(socket)
    set_prot_level(socket)
    get_response(socket)
    set_conn_type(socket)
    get_response(socket)
    set_conn_mode(socket)
    get_response(socket)
    set_conn_file(socket)
    get_response(socket)
    return socket

def get_response(s: socket.SocketType):
    res = recv_full_msg(s)
    print(res)
    return res

#TODO: actually make use of this function
def is_response_error(msg: str):
    #Responses starting with 4, 5, 6 are errors.
    return re.match('[4|5|6]\d+', msg)



def parse_data_channel(msg):
    """Parses the response from the PASV command. Returns a tuple of (ip_address, port_number)"""
    # TODO: CODE = 200? 
    #format: 227 Entering Passive Mode (192,168,150,90,195,149).
    channel_values = msg[msg.index('(') + 1: msg.index(')')].split(',')
    ip_addr = '{}.{}.{}.{}'.format(*channel_values)
    port = (int(channel_values[4]) << 8) + int(channel_values[5])
    return (ip_addr, port)

def init_data_socket(ctrl_channel: socket.SocketType, ftp_operation: Callable[[socket.SocketType, str], Any] , remote_path: str, host: str) -> socket.SocketType:
    # STEP 1
    send_pasv(ctrl_channel)
    response = get_response(ctrl_channel)
    data_channel_addr = parse_data_channel(response)
    print(data_channel_addr)
    # STEP 2
    ftp_operation(ctrl_channel, remote_path)
    # STEP 3
    data_socket = get_socket(data_channel_addr)
    # STEP 4
    res = get_response(ctrl_channel)
    if is_response_error(res):
        print('Error opening data channel. CODE: {}'.format(res))
        data_socket.close()
        return
    # STEP 5
    data_socket = encrypt_socket(data_socket, host)
    return data_socket

def close_data_socket(data_socket: socket.SocketType, download=True):
    if not download:
        print('closing')
        data_socket = data_socket.unwrap()
        data_socket.shutdown(socket.SHUT_WR)

    # data = __recv_data(data_socket)
    # while data:
        # data = __recv_data(data_socket)
    # STEP 7
    # data_socket.sendall('\r\n'.encode())
    # data_socket = encrypt_socket(data_socket,)

    data_socket.close()

def get_file(path, params='wb') -> BinaryIO:
    try:
        file = open(path, params)
        return file
    except OSError as err:
        print('Error with local file or directory, {}'.format(err))



        
def main(args):
    ftp_info = parse_ftp_url(args.params)
    is_download = len(args.params) == 2 and args.params[0].startswith('ftps://')
    remote_path = ftp_info.get(REMOTE)
    local_path = ftp_info.get(LOCAL)
    operation = OPERATIONS_DICT.get(args.operation)
    if not ftp_info:
        return
    socket = get_socket((ftp_info.get(HOST), ftp_info.get(PORT)))
    socket = handle_login(socket, host=ftp_info.get(HOST), username=ftp_info.get(USER), password=ftp_info.get(PASS))
    if operation == MKDIR:
        send_mkd(socket, remote_path)
    elif operation == RMDIR:
        send_rmd(socket, remote_path)
    elif operation == LS:
        # STEP 1 - 5
        data_socket = init_data_socket(socket, send_list, remote_path, ftp_info.get(HOST))
        if not data_socket:
            return
        # STEP 6
        while True:
            data = __recv_data(data_socket)
            if not data: break
            dir_list = data.decode('utf-8')
            print(dir_list)
        # STEP 7, 8
        close_data_socket(data_socket)
    elif operation == CP:
        if is_download:
            data_socket = init_data_socket(socket, send_return, remote_path, ftp_info.get(HOST))
            file = get_file(local_path)
            # STEP 6
            if file:
                data = __recv_data(data_socket)
                while data:
                    file.write(data)
                    data = __recv_data(data_socket)
                file.close()
            close_data_socket(data_socket, is_download)
            get_response(socket)
        else:
            data_socket = init_data_socket(socket, send_store, remote_path, ftp_info.get(HOST))
            # STEP 6
            file = get_file(local_path, 'rb')
            if file:
                data = file.read(4096)
                while data:
                    data_socket.sendall(data)
                    data = file.read(4096)
                # STEP 7
                file.close()
            close_data_socket(data_socket, is_download)
    elif operation == RM:
        remote_path = ftp_info.get(REMOTE)
        send_del(socket, remote_path)
        get_response(socket)
    # STEP 8
    send_quit(socket)
    get_response(socket)
    socket.close()
    
if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    main(args)






