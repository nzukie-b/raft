## Approach

 I mostly followed the suggested implementation approach. I initially used socket.inet_aton for the lowest_ip comparison, but needed to convert the bytes into binary for longest prefix matching. I found that the struct module has methods for packing and unpacking bytes objects. By using this module I was able to get a binary string of an IP, and user this for longest prefix matching.