#!/usr/bin/env python3
import argparse, socket, ssl

HOST = 'ftp.3700.network'
PORT = 21
# USERNAME = 'nzukieb'
# PASSWORD = '0yUNA1Bo6XPG8F3IWhZr'
USERNAME = 'Anonoymous'
PASSWORD = ''

AUTH = 'AUTH', TLS = 'TLS'
USER = 'USER'
PASS = 'PASS'
PBSZ = 'PBSZ'
PROT = 'PROT'
TYPE = 'TYPE'
MODE = 'MODE'
STRU = 'STRU'
LIST = 'LIST'
DEL  = 'DELE'
MKD = 'MKD'
RMD = 'RMD'
STOR = 'STOR'
RETR = 'RETR'
QUIT = 'QUIT'
PASV = 'PASV'

FTP_URL = 'ftps://{}:{}@{}:{}/'.format(USERNAME, PASSWORD, HOST, PORT)

parser = argparse.ArgumentParser()
parser.add_argument('operation', dest='operation', action='store', type=str, 
    help='The operation to execute. Valid operations are ls, rm, rmdir, mkdir, cp, and mv') 
parser.add_argument('params',  dest='params', action='store', nargs='+', 
    help='Parameters for the given operation. Will be one or two paths and/or URLs.')


def __get_socket(tls_encrypt, host, port, timeout=30) -> socket.SocketType:
    if tls_encrypt:
        #Create wrapped socket for TLS connection
        context = ssl.create_default_context()
        sock = socket.create_connection((host, port), timeout=timeout)
        return context.wrap_socket(sock, server_hostname=host)
    else:
        # Create default socket
        return socket.create_connection((host, port), timeout=timeout)

def get_tls_socket(host, port) -> socket.SocketType:
    return __get_socket(tls_encrypt=True, host=host, port=port)

def __recv_msg(sock: socket.SocketType):
    data = sock.recv(8192)
    return data.decode('utf-8')

def recv_full_msg(socket: socket.SocketType):
    msgText = __recv_msg(socket)
    # Read until new line
    while msgText.count('\r\n') == 0:
        msgText += __recv_msg(socket)
    return msgText

def __send_command(sock: socket.SocketType, command, param=None):
    msg = '{} {}\r\n'.format(command, param)
    sock.sendall(msg.encode('utf-8'))


def send_auth(socket: socket.SocketType):
    __send_command(socket, AUTH, TLS)

def send_username(socket: socket.SocketType, username):
    __send_command(socket, USER, username)

def send_password(socket: socket.SocketType, password):
    __send_command(socket, PASS, password)

def set_prot_buffer(socket: socket.SocketType):
    __send_command(socket, PBSZ, 0)

def set_prot_level(socket: socket.SocketType):
    __send_command(socket, PROT, 'P')

def set_conn_type(socket: socket.SocketType):
    __send_command(socket, TYPE, 'I')

def set_stream_conn(socket: socket.SocketType):
    __send_command(socket, MODE, 'S')

def set_file_conn(socket: socket.SocketType):
    __send_command(socket, STRU, 'F')

def send_ls(socket: socket.SocketType, dir_path):
    __send_command(socket, LIST, dir_path)


