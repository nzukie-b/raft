
### DEFAULT ARGS ###
HOST = 'ftp.3700.network'
PORT = 21
# USERNAME = 'nzukieb'
# PASSWORD = '0yUNA1Bo6XPG8F3IWhZr'
USERNAME = 'Anonoymous'
PASSWORD = ''
FTP_URL = 'ftps://{}:{}@{}:{}/'


###  FTP REQUEST COMMANDS ###
AUTH = 'AUTH'
TLS = 'TLS'
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




### FTP CLIENT OPERATIONS ###
MV = 'mv'
LS = 'ls'
RM = 'rm'
RMDIR = 'rmdir'
MKDIR = 'mkdir'
CP = 'cp'
OPS = [MV, LS, RM, RMDIR, MKDIR, CP]

### No switches
OPERATIONS_DICT = dict(zip(OPS, OPS))

