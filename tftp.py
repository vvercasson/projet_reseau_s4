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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(addr)
    while True:
        data,adresse = s.recvfrom(1500)

        data1 = data[0:2]
        data2 = data[2:]

        opcode = int.from_bytes(data1, byteorder='big') # opcode pour la requete

        args = data2.split(b'\x00')                      
        filename = args[0].decode('ascii') 
        mode = args[1].decode('ascii') 

        sServeur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # creation d'un socket de reponse
        sServeur.bind("localhost",33425)
        sServeur.sendto(b'\x00\x04\x00\x00') # ACK de reponse WRQ

        # Requete RRQ
        if opcode == 1:
            #ouverture du fichier envoyé
            file = open(filename,'r')
            message = file.readlines()
            sServeur.sento(b'\x00\x03\x00\x01',message)
        # Requete WRQ
        if opcode == 2:
            dataWRQ,adresseWRQ = sServeur.recvfrom(1500)

            #condition data bien recu
            sServeur.sendto(b'\x00\x04\x00\x01') # ACK de réponse DAT1

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
