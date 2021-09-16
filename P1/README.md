## Approach


I started by initially setting up the parser for the command line arguements. When I first tried to connect to the proj1 network, I sent out the hello message and printed the server response to make check that I was able to connect properly. Next I worked on handling the response loop and making sure that the full message is received. I then worked on wrapping the socket for the TLS connection. I ran into some trouble with this, but I realized that I didn't include the server_hostname for wrap_socket().

While developing I tested my code by printing the communication between my client, such as the result for the COUNT messages, to make sure that I receiveing the full response.