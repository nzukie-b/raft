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

def get_socket(address, timeout=30) -> socket.SocketType:
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
            url = re.split('ftps://', url)[1]
        else:
            is_local = True
        if is_local:
            local_path = path
        else:
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

def handle_login(socket: socket.SocketType, username, password):
    send_username(socket, username)
    get_response(socket)
    send_password(socket, password)
    get_response(socket)

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

# def handle_data_receive(ctrl_channel: socket.SocketType, data_channel: socket.SocketType, ftp_info: dict):
#     remote_path = ftp_info.get(REMOTE)
#     local_path = ftp_info.get(LOCAL)
#     data_socket = get_socket(data_channel_addr)
#     # STEP 4
#     res = get_response(socket)
#     if is_response_error(res):
#         print('Error opening data channel. CODE: {}'.format(res))
#         data_socket.close()
#         return
#     # STEP 5
#     data_socket = encrypt_socket(data_socket, ftp_info.get(HOST))
#     # STEP 6
#     while True:
#         data = __recv_data(data_socket)
#         if not data: break
#         dir_list = data.decode('utf-8')
#         print(dir_list)
#     # STEP 7
#     data_socket.close()
#     print('Data socket closed')

#     # if len(paths) >= 2:
#     #     if paths[0]
#     if False:
#         #TODO: Handle data store
#         pass
#     else:
#         # STEP 1
#         send_pasv(ctrl_channel)
#         response = get_response(ctrl_channel)
#         data_channel_addr = parse_data_channel(response)
#         print(data_channel_addr)
#         # STEP 2
#         send_list(socket, remote_path)
#         # STEP 3
        
#         # STEP 8
#         get_response(socket)

    
        
def main(args):
    ftp_info = parse_ftp_url(args.params)
    remote_to_local = len(args.params) == 2 and args.params[0].startswith('ftps://')
    remote_path = ftp_info.get(REMOTE)
    local_path = ftp_info.get(LOCAL)
    operation = OPERATIONS_DICT.get(args.operation)
    print(operation)
    if not ftp_info:
        return
    socket = get_socket((ftp_info.get(HOST), ftp_info.get(PORT)))
    send_auth(socket)
    get_response(socket)
    socket = encrypt_socket(socket, ftp_info.get(HOST))
    print(args)
    handle_login(socket, ftp_info[USER], ftp_info[PASS])
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
    print(operation)
    if operation == MKDIR:
        send_mkd(socket, remote_path)
    elif operation == RMDIR:
        send_rmd(socket, remote_path)
    elif operation == LS:
        # STEP 1
        send_pasv(socket)
        response = get_response(socket)
        data_channel_addr = parse_data_channel(response)
        print(data_channel_addr)
        # STEP 2
        send_list(socket, remote_path)
        # STEP 3
        data_socket = get_socket(data_channel_addr)
        # STEP 4
        res = get_response(socket)
        if is_response_error(res):
            print('Error opening data channel. CODE: {}'.format(res))
            data_socket.close()
            return
        # STEP 5
        data_socket = encrypt_socket(data_socket, ftp_info.get(HOST))
        # STEP 6
        while True:
            data = __recv_data(data_socket)
            if not data: break
            dir_list = data.decode('utf-8')
            print(dir_list)
        # STEP 7
        data_socket.close()
        print('Data socket closed')
        # STEP 8
        get_response(socket)
    elif operation == CP:
        if remote_to_local:
             # STEP 1
            send_pasv(socket)
            response = get_response(socket)
            data_channel_addr = parse_data_channel(response)
            print(data_channel_addr)
            # STEP 2
            send_retr(socket, remote_path)
            # STEP 3
            data_socket = get_socket(data_channel_addr)
            # STEP 4
            res = get_response(socket)
            if is_response_error(res):
                print('Error opening data channel. CODE: {}'.format(res))
                data_socket.close()
                return
            # STEP 5
            data_socket = encrypt_socket(data_socket, ftp_info.get(HOST))
            # STEP 6
            file = open(local_path, 'wb')
            while True:
                data = __recv_data(data_socket)
                file.write(data)
                if not data: 
                    file.close()
                    break
            # STEP 7
            data_socket.close()
            print('Data socket closed')
            # STEP 8
            get_response(socket)
        else:
             # STEP 1
            send_pasv(socket)
            response = get_response(socket)
            data_channel_addr = parse_data_channel(response)
            print(data_channel_addr)
            # STEP 2
            send_retr(socket, remote_path)
            # STEP 3
            data_socket = get_socket(data_channel_addr)
            # STEP 4
            res = get_response(socket)
            if is_response_error(res):
                print('Error opening data channel. CODE: {}'.format(res))
                data_socket.close()
                return
            # STEP 5
            data_socket = encrypt_socket(data_socket, ftp_info.get(HOST))
            # STEP 6
            file = open(local_path, 'rb')
            data = file.read(8192)
            while data:
                data_socket.sendall(data)
                data = file.read(8192)
            # STEP 7
            file.close()
            data_socket.shutdown(socket.SHUT_WR)
            data_socket.unwrap().close()
            print('Data socket closed')
            # STEP 8
            get_response(socket)

    elif operation == DEL:
        remote_path = ftp_info.get(REMOTE)
        send_del(socket, remote_path)
        
    send_quit(socket)
    get_response(socket)
    socket.close()
    
if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    main(args)






