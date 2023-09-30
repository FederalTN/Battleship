import socket
import json
import BattleClasses

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

client = BattleClasses.Cliente("Federal", localPort)

# barcos del cliente
barcos = {
    "ships": {
        "p": [1,1,0], # cordenada (x,y) y orientación (0: vertical, 1: horizontal)
        "b": [1,2,1],
        "s": [2,3,0]
    }
}

# mensaje
msgFromClient = {
    "action": "c"
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

msg = "Message from Server: {}, {} {} {}".format(receivedJson["response"], receivedJson["action"], receivedJson["status"], receivedJson["position"])
print(msg)