import socket
from os import getcwd
from os.path import getsize, basename
from time import sleep
from hashlib import sha256
from tkinter import Tk, filedialog
import sys

class Client(object):

    def __init__(self, host, port, threads = 0):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threads = threads
        print("Connecting...")
        timeout = 0
        while True:
            try:
                self.sock.connect((self.host, self.port))
                self.recieve()
                break
            except:
                if timeout > 20:
                    self.disconnect(2)

                print("Server cannot be reached at this time")
                timeout += 1
                sleep(2)

        del timeout
        self.sendCommand()

    def sendCommand(self):
        while True:
            command = input("\nPlease enter a command: ")
            print()
            self.sock.sendall(command.lower().encode())
            if command == "help":
                self.recieve()
            elif command == "checksum":
                self.sendFiles()
            elif command == "upload":
                self.uploadFile()
            elif command == "exit":
                self.disconnect(0)
            else:
                self.recieve()


    def sendCount(self):
        """
        The purpose of this function is to send the count of threads to the
        main server, allowing the server to create listening threads so that
        the client can begin uploading multiple files over the socket.
        """
        try:
            print()
            self.sock.send(self.threads.encode())
            print(self.recieve())
        except Exception as e:
            print("Ran into an issue")
            print(e)
            self.disconnect(3)

    def sendFiles(self):
        window = Tk()
        window.withdraw()
        filename = filedialog.askopenfilename(initialdir = getcwd(), title = "select file")
        window.destroy()
        hashed = self.getHash(filename) # Get the has of a filename
        size = getsize(filename)
        with open(filename, "rb") as file:
            print("Sending file:\"{}\"".format(basename(filename)))
            self.sock.send(str(size).encode())
            sleep(2)
            self.sock.send(basename(filename).encode())
            sleep(6)
            self.sock.sendfile(file)
            print("File sent")

        print(hashed)
        self.recieve(1024)


    def getHash(self, filename):
        file = open(filename, "rb")
        hashed = sha256(file.read()).hexdigest()
        file.close()

        return hashed


    def uploadFile(self):
        window = Tk()
        window.withdraw()
        filename = filedialog.askopenfilename(initialdir = getcwd(), title = "select file")
        window.destroy()
        size = getsize(filename)
        with open(filename, "rb") as file:
            print("Uploading file: \"{}\"".format(basename(filename)))
            self.sock.send(str(size).encode())
            sleep(2)
            self.sock.send(basename(filename).encode())
            sleep(6)
            self.sock.sendfile(file)
            print("File sent")

        self.recieve(1024)


    def recieve(self, size = 512):
        print(self.sock.recv(size).decode())

    def disconnect(self, code):
        if code == 2:
            print("Connection time out!")
            self.sock.close()
            sys.exit(code)
        elif code == 3:
            print("Program error...")
            sys.exit(code)
        else:
            print("Disconnecting...")
            self.sock.close()
            sys.exit(code)

if __name__ == "__main__":
    Client("localhost", 9999)
