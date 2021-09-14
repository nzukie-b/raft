import argparse, socket, ssl

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest='port', action='store', type=int, default=27994, help='Port to start listing for connections') 
parser.add_argument('-s', '--ssl', dest='ssl', action='store_true', default=False, help='Whether the client should use a TLS encrypted socket.')
parser.add_argument('hostname', help='Name of the server to connect to') 
parser.add_argument('id', help='NEU ID of the student') 


HELLO = 'ex_string HELLO '
COUNT = 'ex_string COUNT '
BYE = 'ex_string BYE '
FIND = 'FIND'

def send_msg(sock: socket.SocketType, msg):
    sock.sendall(msg.encode('ascii'))

def recv_msg(sock: socket.SocketType):
    data = sock.recv(8192)
    return data.decode('ascii')

def main(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = args.port
    host = args.hostname
    neu_id = args.id
    sock.connect((host, port))
    hello_msg = HELLO + neu_id + '\n'
    send_msg(sock, hello_msg)
    while 1:
        msgText = recv_msg(sock)
        # Read until new line
        while msgText.count('\n') == 0:
            msgText += recv_msg(sock)
        print(msgText)
        msg = msgText.split()
        if(len(msg) < 2):
            send_msg(sock, COUNT + "0\n")
        elif (FIND == msg[1]):
            char = msg[2]
            s_msg = msg[3]
            res = s_msg.count(char)
            print(res)
            send_msg(sock, COUNT + str(res) + "\n")
        elif (BYE == msg[1]):
            print(msgText)
            return

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)