import socket, sys
sys.path.insert(0,"client_data")
from french import *
from _thread import start_new_thread

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print("Connected to:",server_address)
sock.connect(server_address)

def listen_server_thread(sock):
    while True:
        data = sock.recv(4096)
        if not data :
            print('Disconnected')
            break
        else:
            print(CODE[data.decode()])

if __name__ == '__main__':
    #Thread to listen server
    start_new_thread(listen_server_thread,(sock,))

    #Send input messages from stdin (main thread)
    while True:
        msg = sys.stdin.readline()[:-1]
        if msg == "/exit":
            sys.exit()
        else:
            sock.sendall(msg.encode())