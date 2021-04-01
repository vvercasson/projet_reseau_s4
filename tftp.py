"""
TFTP Module.
"""

import socket
import sys

########################################################################
#                          COMMON ROUTINES                             #
########################################################################

# todo

########################################################################
#                             SERVER SIDE                              #
########################################################################


def runServer(addr, timeout, thread):
    # todo
    pass

########################################################################
#                             CLIENT SIDE                              #
########################################################################


def put(addr, filename, targetname, blksize, timeout):
    # Creating the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Uncomment to set the timeout
    s.settimeout(timeout)

    # count data packets
    dataCnt = 1

    # Initializing and sending the write request
    frameWRQ = b'\x00\x02' + filename.encode() + b'\x00octet\x00'
    if blksize != 512:
        frameWRQ += b'blksize\x00' + str(blksize).encode() + b'\x00'
    s.sendto(frameWRQ,addr)

    # Opening the file to send
    file = open(filename,'r')
    if targetname != filename:
        file = open(targetname,'r')
    
    # receive first ACK
    data, serverAddr = s.recvfrom(blksize)
    while True:
        # read from file and send data
        pakcet = file.read(blksize)
        encodedPakcet = pakcet.encode()
        s.sendto(encodedPakcet,addr)

        # receive confirmation
        data, serverAddr = s.recvfrom(1500)

    s.close()

########################################################################


def get(addr, filename, targetname, blksize, timeout):
    # todo
    pass

# EOF
