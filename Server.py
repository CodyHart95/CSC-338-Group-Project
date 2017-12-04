import socket, threading
from hashlib import sha256
import sys
from time import sleep

"""
TODO: Clean up code and remove unnecessary functions

"""


class Server(object):

    # The checksum server is the backend server for the connection with the user
    # It'll be able to not only upload to an onsite database, but also check if
    # a user's file is found within this onsite database. At the moment, there is
    # not direct database implementation at the moment.
    responses = []
    def __init__(self, host, port):

        # The server is initialized with host (default localhost) and port
        # (default port is 9999).
        self.host = host
        self.port = port

        # Initializing the socket. Specified as a TCP connection for file
        # integrity.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # This sets the options of a socket to allow the same coket to be
        # reused should be implement a multiprocessing verison.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Simple callout to show the IP and port that the server is operating on
        print("Starting server on {} port {}".format(
                socket.gethostbyname(self.host), self.port))

        # Binding the socket to the server on host and port.
        self.sock.bind((self.host, self.port))

        # An attribute that will hold the information for each client connected.
        # This will give us info on the connections made for the file sending.
        self.clients = []

        # This will be the dictionary key-value pair that will hold the checksum
        # as the key and the value as a set of file names that have the same
        # binary checksum.
        self.collection = {"f5333a754ddfd949823c167dd96a95a30ae5aeff3bb339b1a666ac9caa80d4f1": "clean"}

        # This sets our server to begin listening for new connections
        self.listen()

    def listen(self):

        # This sets up our listener to allow the server 5 backlog connections in
        # its connection queue.
        self.sock.listen(5)
        while True:

            # This while true statement will constantly look for new connections
            # to accept.
            self.accept()


    def accept(self):

        # This function is meant to accept new clients to the server.
        client, address = self.sock.accept()
        if client:

            # In the case that accepting gives us a client object, we will send
            # print this to the screen of the server and then we will send the
            # client a welcome message.
            print("IP address {} connected".format(address[0]))
            client.sendall("\nWelcome! You've connected to CSC 338's checksum "
                           "server! Enjoy! Send \"help\" for commands".encode())

            # Once we have sent the message to the client, we will append the
            # client to our client list then begin listening to the client for
            # commands.
            self.clients.append((client, address))
            self.listenToClient(client, address)


    def listenToClient(self, client, address):

        # This function is meant to listen to the client for predetermined
        # commands. If the command is not predetermined, we will send them a
        # notification saying that the command is not recognized and ask the
        # client to send "help" in order to see our list of commands.
        while True:
            command = client.recv(256).decode()
            
            
            # If the client sends "checksum," we will check the file they
            # send against the server's "database" and return the results
            # and checksum to the user.
            if command == "checksum":
                numFiles = int(client.recv(10).decode())
            #creates threads that match our incoming threads
            #this allows the server to check if each hash matches while the next checksum is sending
                threads = []
                for i in range(numFiles):
                   t = threading.Thread(name = "File #" + str(i), target = self.checkSum, args = [client])
                   t.start()
                   threads.append(t)
            
                for th in threads:
                    th.join()
                for r in self.responses:
                    client.sendall(r.encode())
                    sleep(.05)
            elif command == "exit":

                # If the client sends "exit," the server will remove the client
                # from the client list, close the connection with the client,
                # then break out of the while loop.
                self.removeClient(client, address)
                client.close()
                self.disconnect() # Just for quick debug purposes
                break
            elif command == "help" or command == "h":

                # If the client sends "help," the server will return to the
                # client a list of commands.
                client.sendall(
"""
Commands are as follows:
upload - upload a file to be entered into the checksum database.
checksum - upload file(s) to be checked against database.
exit - close connection with server.
help (or \"h\") - show a list of commands
"""
.encode())
            else:
                client.sendall("Command not recognized. Send \"help\" for more "
                "details".encode())



    def checkSum(self, client):

        # This function accepts the size of the file, the name of the file,
        # and then checks the file against its database.
       
        # Recieve the size of the file.
        
        sha256Hash = client.recv(64).decode()
       

        # Since the server is currently run and tested internally on the same
        # system, most of the transfer times are instance, which affects the
        # transfer of the file and the integrity of the file. Therefore, we
        # need to sleep after every recieve and every send to ensure that the
        # programs on both sides have the time to process and recieve the info
        # before we continue communication or taint the connection buffer.
        #sleep(2)

        # This loop will collect the size of the file. Since we are incapable of
        # purely knowing the size of each file, we will do integer division.
        # The integer division allows us to figure out the floor division of
        # our recieving block size and the file size. This gives us the minimum
        # amount of times to gather the blocksize, which results in
        # size * blocksize. Since size can still be > blocksize, we must ensure
        # that we get the remainder of the file. That is the + 1.

        # Checks if the hash is in our database and returns the appropriate
        # information to the client along with the checksum so that the client
        # can check if the file was sent succesfully.
    
        if sha256Hash in self.collection:
           ''' client.sendall("Your file was found in our database!\nOther names"
                           " for this file are: {}.\nYour checksum is {}.\n\n"
                           .format(", ".join(self.collection[sha256Hash]),
                           sha256Hash).encode())'''
           self.responses.append("Your file was found in our database!\nOther names"
                           " for this file are: {}.\nYour checksum is {}.\n\n"
                           .format(", ".join(self.collection[sha256Hash]),
                           sha256Hash))
        else:
            '''client.sendall("Your file was not found in our database! :( Please"
                            " upload this file so that others can check against"
                            " it!\nYour checksum is {}.\n\n".format(sha256Hash)
                            .encode())'''
            self.responses.append("Your file was not found in our database! :( Please"
                            " upload this file so that others can check against"
                            " it!\nYour checksum is {}.\n\n".format(sha256Hash))
        #sleep(3)
    

    def removeClient(self, client, address):

        # Removes a client from the clients list and prints to the server
        # that the IP address was disconnected.

        print("IP {} disconnected.".format(address[0]))
        self.clients.remove((client, address))

    def disconnect(self):

        # Disconnects the server from the port.

        print("Closing server down...")
        self.sock.close()
        sys.exit(0)


    def purgeClients(self):

        # A quick purge of the clients list along with disconnecting them.
        # Used on server end before shutting down. Yet to be fully implemented.

        for i in self.clients:
            print("Disconnecting {}".format(i[0]))
            i[0].close()
        del self.clients

if __name__ == "__main__":
    server = Server('localhost', 9999)
