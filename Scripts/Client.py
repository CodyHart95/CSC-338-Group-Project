import socket
from os import getcwd
from os.path import getsize
from time import sleep
from hashlib import sha256

class Client(object):
    number = 0
    def __init__(self, host, port, threads = 0):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num = Client.number
        print("Connecting...")
        try:
            self.sock.connect((self.host, self.port))
            print(self.sock.recv(512).decode())
        except Exception as e:
            print(e)
            
        self.threads = threads
        Client.number += 1
        
    def sendCount(self):
        """
        The purpose of this function is to send the count of threads to the 
        main server, allowing the server to create listening threads so that
        the client can begin uploading multiple files over the socket.
        """
        try:
            self.threads = input("How many files you sendin', boi or grill,"
                                 " I support all people: ")
            print()
            self.sock.send(self.threads.encode())
            print(self.sock.recv(1024).decode())
        except Exception as e:
            print("Ran into an issue")
            print(e)
            self.close()
    
    def sendFiles(self):
        print("Before")
        directory = getcwd()
        filename = directory + "/Favicon/icon.jpg"
        hashed = self.getHash(filename)
        size = getsize(filename)
        print(size)
        with open(filename, "rb") as file:
            print("About to send...")
            self.sock.send(str(size).encode())
            print("Sent size")
            sleep(2)
            self.sock.send(file.name.encode())
            print("Sent file name")
            sleep(2)
            print("Sending file...")
            self.sock.sendfile(file)
            print("File sent")
        
        serverHashed = self.sock.recv(1024).decode()
        print("Server hash recieved.")
        print(hashed)
        print(serverHashed)
        print(hashed == serverHashed)
        file.close()
            
        
    def getHash(self, filename):
        file = open(filename, "rb")
        hashed = sha256(file.read()).hexdigest()
        file.close()
        
        return hashed
    
    def sendNum(self):
        self.sock.sendall("Greetings from socket {}".format(self.num).encode())
    
    def recieve(self):
        print(self.sock.recv(512).decode())
        
    def close(self):
        print("Disconnecting...")
        self.sock.close()

if __name__ == "__main__":
    sock = Client("localhost", 9999)
    sock.sendFiles()
    
    
#    for i in range(50):
#        socks.append(Client("localhost", 9999))
