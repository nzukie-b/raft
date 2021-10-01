## Approach

My approach to this assignment was to first define constants for the commands and functions to send them to the server. Then worked on opening the control socket and handling the initial connection establishment at login. After this I added proper command line parsing instead of my own login info. From here I followed the suggested implementation approach for handling the MKD, RMD, PASV, LIST, STORE, RETR, and DELE commands. Next I did the error handling for server responses. Finally I implemented support for the mv operation since it is just a combination of cp and rm.

Locally, I tested my client's functionality by verifying against FileZilla. After verifying that it worked on my computer, I tested my client on the khoury machines. 
