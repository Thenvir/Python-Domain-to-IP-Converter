import argparse
from sys import argv
import socket
import binascii
import struct

# EXAMPLE:
# python Server.py 5444
# python Client.py vi.cs.rutgers.edu 5444

# Parse the Port number to create server socket
parser=argparse.ArgumentParser(description="""Arg Parser for Server.py""")
parser.add_argument('portNum', type=int, help='This is the port to launch the server on',action='store')
args = parser.parse_args(argv[1:])

portNum = args.portNum

# Create The Server socket // Talk to Client
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.bind(('', portNum))
ss.listen(0)
sock, addr = ss.accept()

# SEND UDP MESSAGE FUNC
def sendUDP(message, address, port):
    # message has to be a hexadecimal encoded string
    message = message.replace(" ", "").replace("\n","")

    server_address = (address, port)
    udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSock.sendto(binascii.unhexlify(message), server_address)
    data, _ = udpSock.recvfrom(4096)

    udpSock.close() # close UDP in same way?
    return binascii.hexlify(data).decode("utf-8")

def charToHex(char):
    return (hex(ord(char)))[2:]

# DOMAIN TO HEX FUNC
def domainToHex(domain):
    sections = (domain.split('.'))

    sectionLen = len(sections)
    i = 0
    label = ''
    ans = ''

    for section in sections:
        # get a label each loop, as well as its length
        label = section
        labelLen = len(label)
        hexLabelLen = '%.2X' % labelLen
        ans = ans + hexLabelLen + ' '

        for element in label:
            ans = ans + charToHex(element) + ' '

    return ans[:-1]

# CONVERT HEX TO IP FUNC
def hexToIP(hex):
    decrement = 2
    ipLen = len(hex)
    ans = ''
    endCounter = 0

    while ipLen>0:
        ans = ans + str(int(hex[:decrement],16))
        ans = ans +'.'
        ipLen = ipLen - decrement
        hex = hex[decrement:]
        endCounter = endCounter + 1
        if(endCounter % 4 == 0 and endCounter != 0 and ipLen != 0):
            ans = ans +', '
    return ans[:-1]
    
def hexBegin(response, cutoff, notFound):
    
    numAnswers = int(response[15])
    responsePart = response[cutoff:]
    ans = ''

    if(notFound == 1):
        ans = ans + hexToIP(response[-8:])
        # print('Converting ' + response[-8:] + ' --> ' + hexToIP(response[-8:]))
        return ans

    # loop through to get all IP's
    while numAnswers > 0:
        ans = ans + hexToIP(responsePart[:8]) + ', '
        # print('Converting ' + responsePart[:8] + ' --> ' + hexToIP(responsePart[:8]))
        # print('NEW Converting ' + '1f0d4724 --> ' + hexToIP('1f0d4724'));
        numAnswers = numAnswers-1
        responsePart = responsePart[24+8:]

    return ans[:-2]

# ------------------- Communication Loop
active = True
# Query: only contain  Header and Question section

header = "AA AA 01 00 00 01 00 00 00 00 00 00 " 

questionTail = " 00 00 01 00 01"

clientString = ''

while active:
    clientString = sock.recv(256)
    clientString = clientString.decode('utf-8')

    if clientString != '':
        headerLen = len(header)
        questionLen = len(domainToHex(clientString))

        message = header + domainToHex(clientString) + questionTail
        messageLen = len(message.replace(" ", ''))
        #print('Message: ' +message + ' with length ' + str(messageLen) )

        response = sendUDP(message, "8.8.8.8", 53)

        # print('Response: ' + response + ' with length ' + str(len(response)))

        finalString = ''
        if(int(response[messageLen+7]) != 1):
            # print(int(response[messageLen+7]))
            finalString = 'not found, ' + hexBegin(response, messageLen+24, 1)
        else:
            finalString = hexBegin(response, messageLen+24, 0)

        sock.sendall(finalString.encode('utf-8'))

    else:
        active = False

# Exit Gracefully
ss.close()
sock.close()