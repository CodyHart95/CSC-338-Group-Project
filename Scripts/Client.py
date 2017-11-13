import socket
from os import getcwd
from os.path import getsize, basename
from time import sleep
from hashlib import sha256
from tkinter import Tk, filedialog
import sys

class Client(object):

    # The client counterpart to the checksum. Includes the interactions for
    # the client and the server.

    def __init__(self, host, port, threads = 0):

        # Currently, the client is initialized with a host to connect to
        # and a port. It also has "threads" which is in anticipation of the
        # threaded connections to the server. However, this may change depending
        # on the suggested implementation or my own implementation (if nothing
        # is done).

        self.host = host
        self.port = port

        # Set up a TCP socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threads = threads
        print("Connecting...")

        # This is a makeshift timeout. This can be done normally using the
        # the socket module, but I wanted to inform the user and customize it
        # so I added my own implementation. Currently, the time out is set to
        # 40 seconds.

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
            elif command == "upload":
                self.uploadFile()
            elif command == "exit":
                self.disconnect(0)
            else:

                # If any other command is sent, be ready to recieve from the
                # server

                self.recieve()


    def sendCount(self):

        # Currently, this function serves no purpose except to be a possible
        # placeholder for future changes.

        try:
            print()
            self.sock.send(self.threads.encode())
            print(self.recieve())
        except Exception as e:
            print("Ran into an issue")
            print(e)
            self.disconnect(3)

    def sendFiles(self):

        # Asks the client to select a file to send. Currently, only implemented
        # to send a single file. This may or may not be the place to parallelize.
        # It depends on how we tackle the threading.

        # Creates a root tkinter window.
        window = Tk()

        # Withdraws the windows, prevent the client from seeing the root window.
        window.withdraw()

        # Create a select file window to get the path to a file with.
        filename = filedialog.askopenfilename(initialdir = getcwd(),
                                              title = "select file")

        # Destroy the tkinter window that we just created.
        window.destroy()

        # This was for testing purposes originally. It was to ensure that the
        # file was sending entirely.
        hashed = self.getHash(filename) # Get the has of a filename

        # Get the size of the file that we are preparing to send.
        size = getsize(filename)

        # Opens our file and prepares to send it.
        with open(filename, "rb") as file:

            # Print to the client the file name of the file that we are sending
            # to the server to be checjed.
            print("Sending file: \"{}\"".format(basename(filename)))

            # Send the size of the file to the server.
            self.sock.send(str(size).encode())

            # Sleep the program in order to give the server time to recieve the
            # size data.
            sleep(2)

            # Send the file name to the server. At the moment, this doesn't
            # serve a purpose, but once we implement the threading on the user
            # side, it'll allow us to see which file the server is returning
            # results for.
            self.sock.send(basename(filename).encode())

            # Sleep again in order to give the server time to recieve the file
            # data.
            sleep(6)

            # Sending the file into the connection buffer.
            self.sock.sendfile(file)

            # Notify the user that the file was sent succesfully. May implement
            # the name of the file to the output so we can see which file was
            # sent when.
            print("File sent")

        # This print is for comparison purposes to ensure that the file sent to
        # the server arrived in tact. Since the server will return the hash of
        # the binary sent to it, we should have a checksum to check against.
        # It should be removed once we ensure that it works in most cases up to
        # a certain data limit (I have yet to test anything over 400KB).
        print(hashed)

        # Recieve the response from the server. For this function, it should be
        # whether the file was found in the database or not.
        self.recieve(1024)


    def getHash(self, filename):

        # This function is simply just getting the SHA256 hash of the file at
        # the path found in "filename."

        file = open(filename, "rb")
        hashed = sha256(file.read()).hexdigest()
        file.close()

        return hashed


    def uploadFile(self):

        # Similar to sendFiles(), this function is meant to ask the user which
        # file they want to send to the server. Primarily, this function
        # is used to differentiate from sendFiles() for purpose. It does
        # basically the same thing, but expects a different output/response
        # from the server. This is not to be parallelized at the moment, but
        # could be. However, that would include threading on the server, which
        # we may not have to do at the moment. Should we want to thread this
        # function, we'll have to be sure to Lock the current implementation
        # of our "database," which is a dictionary. This is to ensure data
        # integrity.

        # Creates the tkinter root window.
        window = Tk()

        # Withdraws the root window so the user does not see it.
        window.withdraw()

        # Creates a file selection dialog box to select which file to upload.
        filename = filedialog.askopenfilename(initialdir = getcwd(),
                                              title = "select file")

        # Destroys the tkinter window object once finished.
        window.destroy()

        # Gets the size of the file.
        size = getsize(filename)

        # Opens the file object.
        with open(filename, "rb") as file:

            # Print to the user which file is about to be sent.
            print("Uploading file: \"{}\"".format(basename(filename)))

            # Sends the size of the file to the server.
            self.sock.send(str(size).encode())

            # Sleep to ensure the server is ready for the next set of data.
            sleep(2)

            # Sends the name of the file to the server so that it can associate
            # the file name with the appropriate hash.
            self.sock.send(basename(filename).encode())

            # Sleep again to ensure the server has time to prepare for the next
            # set of data.
            sleep(6)

            # Send the file to the server.
            self.sock.sendfile(file)

            # Notify the client that the file was sent succesfully.
            print("File sent")

        # Recieve the response from the server. Should be along the lines of
        # "Upload complete!"
        self.recieve(1024)


    def recieve(self, size = 512):

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
