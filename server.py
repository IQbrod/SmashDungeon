import socket
import sys
sys.path.insert(0,"server_data")
from parameters import *
from db_linker import DBL
from _thread import start_new_thread, allocate_lock
from random import randint
import os

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

## SERVER BEHAVIOR ##
clients = []

class User():
    def __init__(self,conn,addr):
        self.conn = conn
        self.addr = addr
        self.name = ""

    def isLoggedIn(self):
        return self.name != ""

def finalexit():
    DBL.exit()
    s.close()
    sys.exit()

def broadcast(msg):
    for client in clients:
        client.conn.sendall(msg.encode())

def generate_world(x,y,n):
    world = []
    for i in range(x):
        world.append([])
        for j in range(y):
            world[i].append(0)

    i=0
    while i < n:
        if world[randint(0,x-1)][randint(0,y-1)] == 0:
            world[randint(0,x-1)][randint(0,y-1)] = 1
            i += 1

    with open(WORLD_FILE, "w") as f:
        for i in range(x):
            for j in range(y):
                f.write(str(world[i][j]))
            f.write("\n")

def server_log(msg):
    with logs_lock:
        with open(LOGS_FILE, "a") as f:
            f.write(msg)
## SERVER FUNCTIONS ## 
def new_user(usr,args):
    # Parse args
    args = args.rstrip("\n").split(",")
    # Send to DBLinker
    res = DBL.adduser(args[0],args[1],args[2])
    # Answer client
    usr.conn.sendall(res.encode())

def log_user(usr,args):
    # Parse args
    args = args.rstrip("\n").split(",")
    # Send to DBLinker
    res = DBL.loguser(args[0],args[1])
    # Log user on server side
    if res is "LOG":
        usr.name = args[0]
    # Answer client
    usr.conn.sendall(res.encode())

def list_account(usr,args):
    # Verify user is logged in
    if not sr.isLoggedIn():
        return "DSC"
    # Send to DBLinked
    res = DBL.listacc(usr.name)
    # Answer client
    usr.conn.sendall(res.encode())

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
        elif cmd == "LOG":
            log_user(usr,args)
        elif cmd == "ACC":
            list_account(usr,args)
        else:
            usr.conn.sendall("UNK".encode())
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
        
#Start main_thread accepting clients

if not os.path.isfile(WORLD_FILE):
    generate_world(9,9,5)

start_new_thread(main_thread,(s,))

while True:
    msg=sys.stdin.readline()[:-1]
    if msg == "/exit":
        finalexit()