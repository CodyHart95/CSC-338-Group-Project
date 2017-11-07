# CSC-338-Group-Project
CSC-338 - Parallel and Distributed group project. 

The basic idea of this project is to create a client-server interaction where the client
sends a file to the server, the server then processes a SHA256 checksum for the file.
The server then checks local databases (at the moment, most likely a dictionary that is
initiated with a file as the main focus of the project has yet to be mentioned) and returns
to the user the results of its process, specifically whether or not the file exists in its
database and the checksum itself (to ensure file integrity). This is to be implemented
by allow multiple connections/socket connections for each file being uploaded to keep
the integrity of each file at bay as well as allowing the server to run these in parallel.
It also allows for some files to be finished processing earlier, merely based on size.
If a 500MB file is being sent over (not sure why you'd be sending over a 500MB file, nonetheless)
and a 10KB file is sent afterwards, in a non-parallelized situation, the 10KB will have
to wait on the 500MB file to be processed and checked before going. Threading the connections
will allow the 500MB file to be sent and processed while the 10KB is also being sent and processed.
The result should be that file 2 (the 10KB file) will have its results returned earlier than file 1
(the 500MB file) simply because of I/O constraints over sockets.
