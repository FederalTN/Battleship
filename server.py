import socket
import json
import BattleClasses

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

server = BattleClasses.Servidor()

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Esperando conexiones entrantes\n")

# Confirmacion del servidor de una accion del usuario
def serverResponse(address, text, body, status, position):
    msgFromServer = {
        "response": text,
        "action": body, # Accion recibida, confirmando
        "status": status,#, # [0: False, 1: True] si la accion del cliente es correcta o no
        "position":  position # utlimas coordenadas jugadas x un usuario
    }
    bytesToSend = json.dumps(msgFromServer).encode()
    UDPServerSocket.sendto(bytesToSend, address)

def serverResponseGlobal(server, text, body, status, position):
    for players in server.jugadoresConectados:
        address = players.address
        serverResponse(address, text, body, status, position)

def printParticipants(server):
    for players in server.jugadoresConectados:
        print(players.nombre)
    print("")

def battleMatch(server):
    matchOngoing = True
    turnCount = 1
    print("Turno jugador: {}".format(turnCount))
    serverResponseGlobal(server, "Es el turno del jugador {}!".format(turnCount), "s", 1, [])
    while(matchOngoing):
        # Recibir acciones de participantes
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        if(("Client {}: {}".format(turnCount, address)) == server.jugadoresConectados[turnCount-1].nombre):
            # Mantiene un orden ciclico de turnos
            if(turnCount == len(server.jugadoresConectados)):
                turnCount = 0
            # Decodifica el mensaje JSON
            receivedJson = json.loads(message.decode())
            clientMsg = receivedJson["action"]

            print(clientMsg)


            # Salta a los perdedores y informa el turno
            turnCount += 1
            while(server.jugadoresConectados[turnCount-1].vida == 0):
                turnCount += 1
            print("Turno jugador: {}".format(turnCount))
            serverResponseGlobal(server, "Es el turno del jugador {}".format(turnCount), "s", 1, [])
            

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
        print("Conexion entrante")

        # Conecta a un jugador
        clientIP = "Client {}: {}".format(len(server.jugadoresConectados)+1, address)
        server.conectarJugador(BattleClasses.Jugador(clientIP, address))

        # Confirma al jugador
        serverResponse(address, "Conexion correcta! Eres el jugador {}".format(len(server.jugadoresConectados)), clientMsg, 1, [])

        # Quienes estan conectados en el server
        print("JUGADORES CONECTADOS:")
        printParticipants(server)
        
    # Verifica si se inicio la partida
    elif (clientMsg == "s"):
        # Confirmacion de inicio de partida
        print("Un jugador dio la orden de empezar una partida")
        serverResponseGlobal(server, "Se empezo la partida!",clientMsg, 1, [])

        # Quienes estan participando de la partida en el server
        print("JUGADORES PARTICIPANTES:")
        printParticipants(server)

        # iniciar partida
        server.iniciarPartida # aun no hace nada xd
        # while de partida en curso
        battleMatch(server)

    else:
        # Comando erroneo
        print("Denegacion de comando entrante")
        serverResponse(address, "Comando erroneo, intente denuevo", clientMsg, 0, [])