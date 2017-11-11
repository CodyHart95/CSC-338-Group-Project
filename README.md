# CSC-338-Group-Project
## Description </h2>
The group project for CSC 338 - Parallel and Distributed Processing.

Our group is **group 6**.


> DUE DATE: Finals day on **December 14 at 11:00 AM - 1:00 PM**.
I will also ask that one of us (or some of us) work on a presentation for the project.
It can be in whatever format (powerpoint, Google slides, whatever) as long as we have access to it so we can be prepared.

## Concept
The basic idea of this project is to create a client-server interaction where the client
sends a file to the server, the server then processes a SHA256 checksum for the file.
The server then checks local databases (at the moment, most likely a dictionary that is
initiated with a file as the main focus of the project has yet to be mentioned) and returns
to the user the results of its process, specifically whether or not the file exists in its
database and the checksum itself (to ensure file integrity). This is to be implemented
by allowing multiple connections/socket connections using threading.
Rach file being uploaded separately will keepthe integrity of each file as well as
allowing the server to run its process in parallel with the I/O bound information.

It also allows for some files to be finished processing earlier, merely based on size.
As an example, a 500MB file is being sent over (not sure why you'd be sending over a 500MB file, nonetheless)
and a 10KB file is sent afterwards, in a non-parallelized situation, the 10KB will have
to wait on the 500MB file to be processed and checked before going. Threading the connections
will allow the 500MB file to be sent and processed while the 10KB is also being sent and processed.
The result should be that file 2 (the 10KB file) will have its results returned earlier than file 1 (the 500MB file)
simply because of I/O constraints over sockets.


## Dependencies 
As of now, the scripts require:
- Python 3.5 (specifically, for socket.sendfile()) or above</li>
- Sockets, hashlib, tkinter, etc. (Most of these things are automatically packaged with the base Python installer) </li>
  
