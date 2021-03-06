"""
TFTP Module.
"""

import socket
import sys
import random

########################################################################
#                          COMMON ROUTINES                             #
########################################################################


def isPortAvailable(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('', port))
        s.close()
        return True
    except:
        return False


def getRandPort():
    while True:
        randomPort = random.randint(10000, 30000)
        if isPortAvailable(randomPort):
            return randomPort

########################################################################
#                             SERVER SIDE                              #
########################################################################


def runServer(addr, timeout, thread):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(addr)
    while True:
        data, adresse = s.recvfrom(1500)
        # Treating the request from the client
        data1 = data[0:2]
        data2 = data[2:]
        cmpt = 1  # compteur des data
        # opcode pour la requete
        opcode = int.from_bytes(data1, byteorder='big')

        args = data2.split(b'\x00')
        filename = args[0].decode('ascii')
        mode = args[1].decode('ascii')

        # Opening the new socket for the transfer
        # creation d'un socket de reponse
        sServeur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        newAvailablePort = getRandPort()
        sServeur.bind(('', newAvailablePort))
        sServeur.settimeout(timeout)

        # RRQ -> READ REQUEST (Server sends data to client)
        if opcode == 1:
            # Log
            print("[myclient:"+str(adresse[1])+" -> "+"myserver:" +
                  str(addr[1])+"] RRQ="+str(data))  # data du client

            file = open(filename, 'rb')  # lecture en bit

            # reading the file
            while True:
                end = False
                if args[2].decode('ascii') == 'blksize':
                    blkSize = args[3].decode('ascii')  # decoupage du message
                    message = file.read(int(blkSize))  # on lit
                    if len(message) != int(blkSize):
                        end = True
                else:
                    message = file.read(512)
                    if len(message) != 512:
                        end = True

                # EOF ?
                # if len(message) == 0:
                #     break

                # Create DAT packet
                msg = b'\x00\x03\x00'
                cmptAsByte = cmpt.to_bytes(1, 'big')
                msg += cmptAsByte
                requete = msg+message
                # print(b"SEND DATA : " + requete)

                # Logs
                # [myserver:port -> myclient:port] DATcmpt=b'\x00\x03\x00\x0cmpt+message'
                print("[myserver:"+str(newAvailablePort)+" -> "+"myclient:" +
                      str(adresse[1])+"] DAT"+str(cmpt)+"="+str(requete))
                

                # Sending
                sServeur.sendto(requete, adresse)

                # Receive ACK
                messageACK, _ = sServeur.recvfrom(1500)
                # print(b"LALALALA : " + messageACK)
                print("[myclient:"+str(adresse[1])+" -> "+"myserver:" +
                      str(newAvailablePort)+"] ACK"+str(cmpt)+"="+str(messageACK))  # reponse ACK

                cmpt += 1  # increment amount of data sent
                if end == True:
                    break

            file.close()

        # WRQ -> WRITE REQUEST (Client sends data to server)
        if opcode == 2:
            firstACK = b'\x00\x04\x00\x00'
            if args[2].decode('ascii') == 'blksize':
                blkSize = args[3].decode('ascii')  # decoupage du message
            else:
                blkSize = 512
            sServeur.sendto(firstACK, adresse)  # ACK answer to the WRQ
            print("[myclient:"+str(adresse[1])+" -> " +
                  "myserver:"+str(addr[1])+"] WRQ="+str(data))
            print("[myserver:"+str(newAvailablePort)+" -> " +
                  "myclient:"+str(adresse[1])+"] ACK0="+str(firstACK))

            file = open(filename, 'wb')  # Opening the file to write in

            while True:
                # Receiving data
                try:
                    dataWRQ = sServeur.recvfrom(1500)
                except socket.timeout:
                    break
                # print(dataWRQ[0].decode())

                # Writing data in file
                file.write(dataWRQ[0][4:])

                msg = b'\x00\x04\x00'
                cmptAsByte = cmpt.to_bytes(1, 'big')
                msg += cmptAsByte
                print("[myclient:"+str(adresse[1])+" -> "+"myserver:" +
                      str(newAvailablePort)+"] DAT"+str(cmpt)+"="+str(dataWRQ[0]))
                print("[myserver:"+str(33425)+" -> "+"myclient:" +
                      str(adresse[1])+"] ACK"+str(cmpt)+"="+str(msg))
                sServeur.sendto(msg, adresse)
                if len(dataWRQ[0][4:]) != blkSize:
                    break
                cmpt += 1

            file.close()

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
    s.sendto(frameWRQ, addr)

    # Opening the file to send
    file = open(filename, 'rb')

    # receive first ACK
    # messageACK, serverAddr = s.recvfrom(1500)
    while True:
        # Receive ACKs
        messageACK, serverAddr = s.recvfrom(1500)
        print(b"MESSAGE ACK RECU : "+messageACK)

        # read from file and send data
        pakcet = file.read(blksize)
        if len(pakcet) == 0:
            break
        msgToSend = b'\x00\x03\x00'
        cmptByte = dataCnt.to_bytes(1, 'big')
        msgToSend += cmptByte
        msgToSend += pakcet
        dataCnt += 1
        print(b"MESSAGE SENT : " + msgToSend)

        s.sendto(msgToSend, serverAddr)

        # receive confirmation
        
    s.close()

########################################################################


def get(addr, filename, targetname, blksize, timeout):
    # Creating the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Uncomment to set the timeout
    s.settimeout(timeout)

    # count data packets
    dataCnt = 1

    # Initializing and sending the write request
    frameRRQ = b'\x00\x01' + filename.encode() + b'\x00octet\x00'
    if blksize != 512:
        frameRRQ += b'blksize\x00' + str(blksize).encode() + b'\x00'
    s.sendto(frameRRQ, addr)
    # Opening the file to write in
    # file = open(targetname,'w')
    file = open(targetname, 'wb')
    

    while True:
        # receive data
        try:
            data, serverAddr = s.recvfrom(1500)
            messageACK = b'\x00\x04\x00'
            cmptByte = dataCnt.to_bytes(1, 'big')
            messageACK += cmptByte
            dataCnt += 1
            # print(b"ACK envoye : " + messageACK)

            s.sendto(messageACK, serverAddr)

        except socket.timeout:
            break
        file.write(data[4:])  # Should check
        print(b'received message : ' + data)
        print(b'written part :' + data[4:])
        if len(data[4:]) != blksize:
            break
    s.close()

# EOF
