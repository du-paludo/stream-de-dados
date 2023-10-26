import socket

localIP = "127.0.0.1"
localPort = 5968
bufferSize = 1024
msgFromServer = "Hello UDP Client"
bytesToSend = str.encode(msgFromServer)

socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket.bind((localIP, localPort))

print("UDP server up and listening")

while (True):
    bytesAddressPair = socket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    clientMsg = "Message from Client: {}".format(message)
    clientIP = "Client IP Address: {}".format(address)

    print(clientMsg)
    print(clientIP)

    socket.sendto(bytesToSend, address)