import socket
import json

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

msgFromServer = {
    "response": "HELLO UDP CLIENT"
}
bytesToSend = json.dumps(msgFromServer).encode()

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    # Decodifica el mensaje JSON
    receivedJson = json.loads(message.decode())

    clientMsg = "Message from Client:{}".format(receivedJson["message"])
    clientIP = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)