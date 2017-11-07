from tkinter import filedialog
from tkinter import *
import Client
import threading
from os import getcwd


class UserWindow(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.master.geometry("400x300")
        self.master.resizable(width = False, height = False)
        self.master.title("Checksum")
        self.grid()

        self.connectFrame = Frame(self, width = 400, height = 300, bg = "black")
        self.connectFrame.grid(row = 0, column = 0)
        #Create the Label describing what to do.
        self._instruct = Label(self.connectFrame,
                               text = "IP address:Port Number",
                               fg = "white",
                               bg = "black",
                               font = "Arial")
        self._instruct.place(relx = .5, rely = .33, anchor = 'c')
        # Create the IP entry field.
        self._IPVar = StringVar(value = "127.0.0.1:9999")
        self._IPEntry = Entry(self.connectFrame, textvariable = self._IPVar)
        self._IPEntry.place(relx = .5, rely = .4, anchor = 'c')

        # Creates a button to initiate connection to the server
        self._initiate = Button(self.connectFrame,
                                text = "Connect",
                                command = self._connect)
        self._initiate.place(relx = .5, rely = .5, anchor = 'c')
        
        self._select = Button(self.connectFrame,
                               text = "File Selection",
                               command = self._chooseFiles)
        
        self._select.place(relx = .5, rely = .75, anchor = 'c')
        # Creates an exit button that allows you to close the window.
        self._leave = Button(self.connectFrame,
                             text = "Exit",
                             command = self._exit,
                             width = 55)
        self._leave.place(relx = .5, rely = .95, anchor = 'c')
        
        self.master.iconbitmap(r'{}\Favicon\icon.ico'.format(getcwd()))
    
    def _chooseFiles(self):
        self.files = filedialog.askopenfilenames(initialdir = "/",
                                        title = "Select Files")
        print(len(self.files))

    def _connect(self):
        host, port = self._IPVar.get().split(":")
        threading.Thread(target = self.createSocket,
                         args = (host, port)).start()
    
    def createSocket(self, host, port):
        self.sock = Client.Client(host, int(port))
    
    def _exit(self):
        try:
            self.sock.close()
            self.master.destroy()
        except:
            self.master.destroy()

def main():
    UserWindow().mainloop()

main()
