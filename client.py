import socket
import json

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

msgFromClient = {
    "message": "HELLO UDP SERVER"
}
bytesToSend = json.dumps(msgFromClient).encode()

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, (localIP, localPort))
# Recibe respuesta
msgFromServer = UDPClientSocket.recvfrom(bufferSize)

# Decodifica el mensaje JSON
receivedJson = json.loads(msgFromServer[0].decode())

msg = "Message from Server {}".format(receivedJson["response"])
print(msg)