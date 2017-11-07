import socket, threading
from hashlib import sha256

from time import sleep
"""
TODO: Implement threading of files/listeners. Might include some research.
TODO: Possibly implement multiprocessing. Will also include research.
"""


class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print("Starting server on {} port {}".format(
                socket.gethostbyname(self.host), self.port))
        self.sock.bind((self.host, self.port))
        
        self.clients = []
        
        self.collection = {}
    
    def listen(self):
        self.sock.listen(5)
        while True:
            self.accept()
#            client, address = self.sock.accept()
#            if client:
#                print("IP address {} connected".format(address[0]))
#                client.sendall("Welcome! You've connected to CSC 338's checksum "
#                           "server! Enjoy!".encode())
            
#            self.listenToClient(client)
#            self.purgeClients()

        
    def accept(self):
        client, address = self.sock.accept()
        if client:
            print("IP address {} connected".format(address[0]))
            client.sendall("Welcome! You've connected to CSC 338's checksum "
                           "server! Enjoy! send \"help\" for commands".encode())
            self.clients.append((client, address))
#            self.recieve(client)
            
    
    def listenToClient(self, client):
        while True:
            command = client.recv(512).decode().lower()
            if command == "upload":
                self.saveFile(client)
            elif command == "checksum":
                self.checkSum(client)
            elif command == "exit":
                self.removeClient(client)
                client.close(client)
                break
            elif command == "help" or command == "h":
                client.sendall(
"""
Commands are as follows:
upload - upload a file to be entered into the checksum database.
checksum - upload file(s) to be checked against database.
exit - close connection with server.
help - show a list of commands
""".encode())
            else:
                client.sendall("Command not recognized.".encode())
            
        
            
    def checkSum(self, client):
        size = client.recv(512).decode()
        sleep(4)
        blocksize = 4096
        file = b''
        for i in range((int(size) // blocksize) + 1):
            file += client.recv(blocksize)
        
        sha256Hash = sha256(file).hexdigest()
        client.sendall("File recieved!".encode())
        if sha256Hash in self.collection:
            client.sendall("Your file was found in our database! Other names"
                           " for this file are {}. Your checksum is {}."
                           .format(self.collection[sha256Hash][0:], sha256Hash)
                           .encode())
        else:
            client.sendall("Your file was not found in our database! :( Please"
                            " upload this file so that others can check it! :)"
                            .encode())
                
        sleep(2)
    
    def saveFile(self, client):
        size = client.recv(512).decode()
        sleep(2)
        filename = client.recv(512).decode()
        blocksize = 4096
        file = b''
        for i in range((int(size) // blocksize) + 1):
            file += client.recv(blocksize)
        
        sha256Hash = sha256(file).hexdigest()
        client.sendall("Upload complete!".encode())
        
        if sha256Hash not in self.collection:
            self.collection[sha256Hash] = [filename]
        else:
            self.collection[sha256Hash].append(filename)
        
        sleep(2)
        
    def removeClient(self, client):
        self.clients.remove(client)

    def close(self):
        self.sock.close()
    
    def recieve(self, client):
        print(client.recv(512).decode())
        client.sendall("Welcome!".encode())
    
    def purgeClients(self):
        for i in self.clients:
            print("Disconnecting {}".format(i[0]))
            i[0].disconnect
        del self.clients
        self.clients = []

if __name__ == "__main__":
    server = Server('localhost', 9999)
    server.listen()
    
