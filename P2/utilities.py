import socket
from constants import *
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
def set_conn_mode(socket: socket.SocketType):
    __send_command(socket, MODE, 'S')
def set_conn_file(socket: socket.SocketType):
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
def send_retr(socket: socket.SocketType, file_path):
    __send_command(socket, RETR, file_path)
def send_quit(socket: socket.SocketType):
    __send_command(socket, QUIT, '')
def send_pasv(socket: socket.SocketType):
    __send_command(socket, PASV, '')
