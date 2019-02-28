import socket
import sys
sys.path.insert(0,"server_data")
from parameters import *
from _thread import start_new_thread, allocate_lock

## SERVER DEFINITION ##
HOST = 'localhost' # all availabe interfaces
PORT = 10000 # arbitrary non privileged port 

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except(socket.error, msg):
    print("Could not create socket. Error Code: ", str(msg[0]), "Error: ", msg[1])
    sys.exit(0)

print("[-] Socket Created")

# bind socket
try:
    s.bind((HOST, PORT))
    print("[-] Socket Bound to port " + str(PORT))
except(socket.error, msg):
    print("Bind Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]))
    sys.exit()

s.listen(10)
#s.settimeout(60)
print("Listening...")

## SERVER LOCKERS ##
logs_lock = allocate_lock()
users_lock = allocate_lock()

## SERVER BEHAVIOR ##
clients = []

class User():
    def __init__(self,conn,addr):
        self.conn = conn
        self.addr = addr
        self.id = -1

def broadcast(msg):
    for client in clients:
        client.conn.sendall(msg.encode())

def server_log(msg):
    with logs_lock:
        with open(LOGS_FILE, "a") as f:
            f.write(msg)

def new_user(usr,args):
    args = args.rstrip("\n").split(",")    

    with users_lock:
        with open(USER_DB, "r+") as f:
            idx = 0
            for line in f:
                l = line.split(",")
                # Same Username
                if (l[1] == args[0]):
                    usr.conn.sendall("NWU".encode())
                    return
                # Same Email
                elif (l[2] == args[1]):
                    usr.conn.sendall("NWM".encode())
                    return
                idx += 1
            # User Creation
            f.write(str(idx)+","+args[0]+","+args[1]+","+args[2]+"\n")
        usr.id = idx
    usr.conn.sendall("NEW".encode())



def client_thread(usr):
    while True:
        # Receive a message
        data = usr.conn.recv(1024)
        # Log the message
        log = "[" + str(usr.addr) + "]: " + data.decode() + "\n"
        server_log(log)

        # Answer
        cmd = data.decode()[:3]
        args = data.decode()[4:]

        if cmd == "NEW":
            new_user(usr,args)
        else:
            usr.conn.sendall("UKN".encode())
    usr.conn.close()

def main_thread(sock):
    while True:
            try:
                conn, addr = sock.accept()
                log = "[-] Connected to " + addr[0] + ":" + str(addr[1])+"\n"
                server_log(log)
                print(log)
                u = User(conn,addr)
                clients.append(u)

                start_new_thread(client_thread, (u,))

            except SystemExit:
                break
                sock.close()

#Start main_thread accepting clients
start_new_thread(main_thread,(s,))

while True:
    msg=sys.stdin.readline()[:-1]
    if msg == "/exit":
        sys.exit()