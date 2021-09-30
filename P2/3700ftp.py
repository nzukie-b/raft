#!/usr/bin/env python3
import argparse, socket
from typing import Any, Callable
from constants import *
from utilities import *

parser = argparse.ArgumentParser()
parser.add_argument('operation', action='store', type=str, 
    help='The operation to execute. Valid operations are ls, rm, rmdir, mkdir, cp, and mv') 
parser.add_argument('params', action='store', nargs='+', 
    help='Parameters for the given operation. Will be one or two paths and/or URLs.')

def recv_data(sock: socket.SocketType):
    data = sock.recv(8192)
    return data

def __recv_full_msg(socket: socket.SocketType):
    msgText = recv_data(socket).decode('utf-8')
    # Read until end of response
    while msgText.count('\r\n') == 0:
        msgText += recv_data(socket)
    return msgText

def get_ctrl_response(s: socket.SocketType):
    res = __recv_full_msg(s)
    print(res)
    return res

def handle_login(socket: socket.SocketType, host:str , username:str, password: str) -> socket.SocketType:
    send_auth(socket)
    get_ctrl_response(socket)
    socket = encrypt_socket(socket, host)
    send_username(socket, username)
    get_ctrl_response(socket)
    send_password(socket, password)
    get_ctrl_response(socket)
    set_prot_buffer(socket)
    get_ctrl_response(socket)
    set_prot_level(socket)
    get_ctrl_response(socket)
    set_conn_type(socket)
    get_ctrl_response(socket)
    set_conn_mode(socket)
    get_ctrl_response(socket)
    set_conn_file(socket)
    get_ctrl_response(socket)
    return socket

def init_data_socket(ctrl_channel: socket.SocketType, ftp_operation: Callable[[socket.SocketType, str], Any] , remote_path: str, host: str) -> socket.SocketType:
    # STEP 1
    send_pasv(ctrl_channel)
    response = get_ctrl_response(ctrl_channel)
    data_channel_addr = parse_data_channel(response)
    # STEP 2
    ftp_operation(ctrl_channel, remote_path)
    # STEP 3
    data_socket = get_socket(data_channel_addr)
    # STEP 4
    res = get_ctrl_response(ctrl_channel)
    if is_response_error(res):
        print('Error opening data channel. CODE: {}'.format(res))
        data_socket.close()
    else:
    # STEP 5
        data_socket = encrypt_socket(data_socket, host)
    return data_socket

def close_data_socket(data_socket: socket.SocketType, download=True):
    #Step 7, 8
    if not download:
        print('closing')
        data_socket = data_socket.unwrap()
        data_socket.shutdown(socket.SHUT_WR)
    data_socket.close()
        
def handle_shutdown(socket: socket.SocketType):
    send_quit(socket)
    get_ctrl_response(socket)
    socket.close()

def main(args):
    ftp_info = parse_ftp_paths(args.params)
    is_download = len(args.params) == 2 and args.params[0].startswith('ftps://')
    remote_path = ftp_info.get(REMOTE)
    local_path = ftp_info.get(LOCAL)
    operation = OPERATIONS_DICT.get(args.operation)
    socket = get_socket((ftp_info.get(HOST), ftp_info.get(PORT)))
    socket = handle_login(socket, host=ftp_info.get(HOST), username=ftp_info.get(USER), password=ftp_info.get(PASS))
    
    # TODO: HANDLE SERVER ERROR RESPONSES
    if operation == MKDIR:
        send_mkd(socket, remote_path)
    elif operation == RMDIR:
        send_rmd(socket, remote_path)
    elif operation == LS:
        # STEP 1 - 5
        data_socket = init_data_socket(socket, send_list, remote_path, ftp_info.get(HOST))
        if data_socket.fileno() == -1:
            handle_shutdown(socket)
            return
        # STEP 6
        while True:
            data = recv_data(data_socket)
            if not data: break
            dir_list = data.decode('utf-8')
            print(dir_list)
        # STEP 7
        close_data_socket(data_socket)
    elif operation == CP:
        data_socket = init_data_socket(socket, send_return, remote_path, ftp_info.get(HOST))
        if data_socket.fileno() == -1:
            handle_shutdown(socket)
            return
        if is_download:
            file = get_file(local_path, 'wb')
            # STEP 6
            if file:
                data = recv_data(data_socket)
                while data:
                    file.write(data)
                    data = recv_data(data_socket)
            # STEP 7
                file.close()
            close_data_socket(data_socket, is_download)
        else:
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
    # STEP 8
    get_ctrl_response(socket)
    handle_shutdown(socket)
    
if __name__ == '__main__':
    args = parser.parse_args()
    if not valid_operation(args):
        print('Invalid operation received: {}'.format(args.operation))
        quit()
    print(args)
    main(args)
