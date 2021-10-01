import socket, re, os, ssl
from constants import *
from typing import BinaryIO
from urllib.parse import urlparse

# Socket creation
def get_socket(address: tuple, timeout=30) -> socket.SocketType:
    sock = socket.create_connection(address, timeout=timeout)
    return sock
def encrypt_socket(socket: socket.SocketType, host) -> socket.SocketType:
    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(socket, server_hostname=host)
    return wrapped_socket
def recv_data(sock: socket.SocketType):
    data = sock.recv(8192)
    return data


### Server Commands
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
def send_store(socket: socket.SocketType, file_path):
    __send_command(socket, STOR, file_path)
def send_return(socket: socket.SocketType, file_path):
    __send_command(socket, RETR, file_path)
def send_quit(socket: socket.SocketType):
    __send_command(socket, QUIT, '')
def send_pasv(socket: socket.SocketType):
    __send_command(socket, PASV, '')


# VALIDATION
def valid_operation(args: tuple) -> bool:
    op = args.operation
    return op in OPS
def is_response_error(msg: str):
    #Responses starting with 4, 5, 6 are errors.
    return re.match('[4|5|6]\d+', msg)


### Parsers
def parse_ftp_paths(params: list) ->  dict:
    # TODO: urllib.parse does this better.
    """Parses the paths and returns a dict of <usernaem"""
    user = DEFAULT_USER
    pword = DEFAULT_PASSWORD
    port = DEFAULT_PORT
    remote_path = None
    local_path = None
    parsed_urls = [urlparse(param) for param in params]
    for url in parsed_urls:
        is_local = False if url.scheme == 'ftps' else True
        if is_local:
            local_path = os.path.join(os.getcwd(), url.path)
        elif '@' in url.netloc:
            url_info = re.split('@', url.netloc)
            login_info = url_info[0]
            if ':' in login_info:
                login_info = re.split(':', login_info)
                if login_info[0]: user = login_info[0]
                if login_info[1]: pword = login_info[1]
            else:
                user = login_info
            host = url_info[1]
            if ':' in host:
                host_info = re.split(':', url)
                host = host_info[0]
                port = host_info[1]
                
            remote_path = url.path if url.path else '/'
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

def parse_data_channel(msg):
    """Parses the response from the PASV command. Returns a tuple of (ip_address, port_number)"""
    # TODO: CODE = 200? 
    #format: 227 Entering Passive Mode (192,168,150,90,195,149).
    channel_values = msg[msg.index('(') + 1: msg.index(')')].split(',')
    ip_addr = '{}.{}.{}.{}'.format(*channel_values)
    port = (int(channel_values[4]) << 8) + int(channel_values[5])
    print(ip_addr, port)
    return (ip_addr, port)

def get_file(path, params='wb') -> BinaryIO:
    try:
        file = open(path, params)
        return file
    except OSError as err:
        print('Error with local file or directory, {}'.format(err))
        return None
