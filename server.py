import socket
import sys
from _thread import start_new_thread

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
s.settimeout(60)
print("Listening...")



## SERVER BEHAVIOR ##
clients = []

class User():
    def __init__(self,conn,addr):
        self.conn = conn
        self.addr = addr
        self.name = ""

def broadcast(msg):
    for client in clients:
        client.conn.sendall(msg.encode())

def client_thread(usr):
    while True:
        data = usr.conn.recv(1024)
        name = usr.name if usr.name != "" else str(usr.addr)
        reply = "[" + name + "]: " + data.decode()
        broadcast(reply)
        if data.decode() == 'Bye':
            break
    conn.close()

def main_thread(sock):
    while True:
            try:
                conn, addr = sock.accept()
                print("[-] Connected to " + addr[0] + ":" + str(addr[1]))
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
    if msg == "exit":
        sys.exit()