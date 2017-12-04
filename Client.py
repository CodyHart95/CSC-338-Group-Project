import socket
from os import getcwd
from os.path import getsize, basename
from time import sleep
from hashlib import sha256
from tkinter import Tk, filedialog
import sys
import threading



class Client(object):

    # The client counterpart to the checksum. Includes the interactions for
    # the client and the server.
    def __init__(self, host, port):

        # Currently, the client is initialized with a host to connect to
        # and a port. It also has "threads" which is in anticipation of the
        # threaded connections to the server. However, this may change depending
        # on the suggested implementation or my own implementation (if nothing
        # is done).

        self.host = host
        self.port = port

        # Set up a TCP socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting...")

        # This is a makeshift timeout. This can be done normally using the
        # the socket module, but I wanted to inform the user and customize it
        # so I added my own implementation. Currently, the time out is set to
        # 40 seconds.

        timeout = 0
        while True:
            try:
                self.sock.connect((self.host, self.port))
                self.receive()
                break
            except:
                if timeout > 20:
                    self.disconnect(2)

                print("Server cannot be reached at this time")
                timeout += 1
                sleep(2)

        # Just to ensure this little bit fo data is destroyed.
        del timeout

        # sendCommand will ask the user for input to send to the server.
        self.sendCommand()
        
    def sendCommand(self):

        # Infinite loop to ask for user interactions.

        while True:

            print(50 * "-")

            # Get commands from the client.
            command = input("\nPlease enter a command: ").lower()
            print()

            print(50 * "-")
            # Ensures that the command is sent with some convention (all lower
            # case letters).
            self.sock.sendall(command.encode())
            if command == "help":
                self.recieve()
            elif command == "checksum":
                self.sendFiles()                     
            elif command == "exit":
                self.disconnect(0)
            else:

                # If any other command is sent, be ready to recieve from the
                # server
                self.receive
    responses = []
    def sendFiles(self):
        # Asks the client to select a file to send. Currently, only implemented
        # to send a single file. This may or may not be the place to parallelize.
        # It depends on how we tackle the threading.

        # Creates a root tkinter window.
        window = Tk()

        # Withdraws the windows, prevent the client from seeing the root window.
        window.withdraw()

        # Create a select file window to get the path to a file with.
        filenames = filedialog.askopenfilenames(initialdir = getcwd(),
                                              title = "select file")

        # Destroy the tkinter window that we just created.
        window.destroy()

        # Hash the files
        hashes = []
        for file in filenames:
            hashes.append(self.getHash(file)) # Get the hash of a filename

        #send the number of files over to the server so it knows how many threads to create
        self.sock.send(str(len(hashes)).encode())

        #This section handles the thread creation that will send the hashes to the server
        
        threads = []
        for h in hashes:
            t = threading.Thread(name = h, target = self.sendHashes, args = [h])
            t.start()
            threads.append(t)
        for th in threads:
            th.join()
    def sendHashes(self,hashed):
       

        # Sends a new checksum command for each thread 
        #command = "checksum"
        #self.sock.sendall(command.encode())
        self.sock.send(hashed.encode())

        # Notify the user that the file was sent succesfully. May implement
        # the name of the file to the output so we can see which file was
        # sent when.
        print("File Sent!\n")

        # Recieve the response from the server. For this function, it should be
        # whether the file was found in the database or not.
        # Also adds them to our responses list so that they can be printed once
        # we have them all.
        #self.responses.append(self.sock.recv(199).decode())
        self.receive(199)
    def getHash(self, filename):

        # This function is simply just getting the SHA256 hash of the file at
        # the path found in "filename."

        file = open(filename, "rb")
        hashed = sha256(file.read()).hexdigest()
        file.close()

        return hashed

    def receive(self, size = 512):

        # This functions only purpose is to help assist in printing recieved
        # data to the client screen. It's more a helper function to prevent
        # having to write self.sock.recv(<buffer>).
        # The default buffer block size to recieve is 512, but can be passed
        # in when the function is called.
        print(self.sock.recv(size).decode())
    def disconnect(self, code):

        # This function is supposed to disconnect the client from the server
        # I added error codes and system exit codes to allow for diagnosis
        # of the reason for disconnecting.
        #
        # Code 2 - Connection time out, the server either never responded, is
        #          busy, or the server could not be reached. Connection issues.
        # Code 3 - The program encountered an error, something went wrong while
        #          running the program that caused it to terminate.
        # Code 0 - Program terminated succesfully. No error was met and the
        #          the program was succesful in closing out.

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
