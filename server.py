import socket
import json
import BattleClasses

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024
server = BattleClasses.Servidor()

msgFromServer = {
    "response": "HELLO UDP CLIENT",
    "action": "c, a, l, b, d, s", # Accion recibida, confirmando
    "status": "0, 1"#, # [0: False, 1: True] si la accion del cliente es correcta o no
#   "position":  [x,y] # utlimas coordenadas jugadas x un usuario
}
bytesToSend = json.dumps(msgFromServer).encode()

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Esperando conexiones entrantes")

# Responde del servidor
def serverResponse(body):
    msgFromServer = {
        "response": body
    }
    bytesToSend = json.dumps(msgFromServer).encode()
    UDPServerSocket.sendto(bytesToSend, address)

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    # Decodifica el mensaje JSON
    receivedJson = json.loads(message.decode())
    clientMsg = receivedJson["action"]

    # Verifica si es una conexion
    if(clientMsg == "c"):
        # Confirmación de conexión
        print("Conexion entrante")
        serverResponse("conexion confirmada")

        # Conecta a un jugador
        clientIP = "Client IP Address:{}".format(address)
        player = BattleClasses.Jugador(clientIP)
        server.conectarJugador(player)

        # Quienes estan conectados en el server
        print("JUGADORES CONECTADOS:")
        for players in server.jugadoresConectados:
            print(players.nombre)
    else:
        # Comando erroneo
        print("Denegacion de comando entrante")
        serverResponse("Comando denegado")