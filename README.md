# Python Domain to IP Converter

When client.py and server.py are run:

- Takes the Domains given in source_strings.txt 

- Converts them to their IP addresses by communicating with Google's DNS server at 8.8.8.8 via UDP packets

- The results are then sent back via TCP packets to the client and stored in the results.txt file.

Inspired by James from https://routley.io/posts/hand-writing-dns-messages/
