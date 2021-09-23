#!/usr/bin/env python3
import argparse, socket, ssl, re
from enum import Enum
from typing import Tuple

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

FTP_URL = 'ftps://{}:{}@{}:{}/'

parser = argparse.ArgumentParser()
parser.add_argument('operation', dest='operation', action='store', type=str, 
    help='The operation to execute. Valid operations are ls, rm, rmdir, mkdir, cp, and mv') 
parser.add_argument('params',  dest='params', action='store', nargs='+', 
    help='Parameters for the given operation. Will be one or two paths and/or URLs.')

def get_socket(host, port, timeout=30) -> socket.SocketType:
    sock = socket.create_connection((host, port), timeout=timeout)
    return sock

def encrypt_socket(socket: socket.SocketType) -> socket.SocketType:
    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(socket, server_hostname=HOST)
    return wrapped_socket

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
def send_list(socket: socket.SocketType, dir_path):
    __send_command(socket, LIST, dir_path)
def send_del(socket: socket.SocketType, file_path):
    __send_command(socket, DEL, file_path)
def send_mkd(socket: socket.SocketType, dir_path):
    __send_command(socket, MKD, dir_path)
def send_rmd(socket: socket.SocketType, dir_path):
    __send_command(socket, RMD, dir_path)
def send_file(socket: socket.SocketType, file_path):
    __send_command(socket, STOR, file_path)
def download_file(socket: socket.SocketType, file_path):
    __send_command(socket, RETR, file_path)
def send_quit(socket: socket.SocketType):
    __send_command(socket, QUIT, '')
def send_pasv(socket: socket.SocketType):
    __send_command(socket, PASV, '')


class Command(Enum):
    MOVE = 'mv'
    LIST = 'ls'
    DEL = 'rm'
    RMD = 'rmdir'
    MKD = 'mkdir'
    COPY = 'cp'

def run():
    pass


def parse_ftp_url(url) -> Tuple:
    """Parses the ftp url and returns a tuple of the format: (ftps, <user>, <password>, HOST</path/to/file>)
        
        Tuples of length 2 don't have user or password fields, length 3 doesn't have password."""
    temp_url = url.replace('://', ':')
    res = tuple(re.split('[:@HOST]', temp_url))
    return res

def parse_data_channel(msg):
    """Parses the response from the PASV command. Returns a tuple of (ip_address, port_number)"""
    # TODO: CODE = 200? 
    #format: 227 Entering Passive Mode (192,168,150,90,195,149)
    channel_values = [int(a) for a in msg[msg.index('(') + 1: -2].split(',')]
    ip_addr = '{}.{}.{}.{}'.format(*channel_values)
    port = (channel_values[4] << 8) + channel_values[5]
    return (ip_addr, port)




def main(args):
    socket = get_socket(HOST, PORT)
    print(recv_full_msg(socket))
    send_auth(socket)
    print(recv_full_msg(socket))
    socket = encrypt_socket(socket)






