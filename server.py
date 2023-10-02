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
        "response": text, # Mensaje del servidor que se enviara ademas de la accion
        "action": body, # Accion recibida, confirmando
        "status": status,#, # [0: False, 1: True] si la accion del cliente es correcta o no
        "position":  position # utlimas coordenadas jugadas x un usuario
    }
    bytesToSend = json.dumps(msgFromServer).encode()
    UDPServerSocket.sendto(bytesToSend, address)
# Enviar un response a todos los jugadores conectados
def serverResponseGlobal(server, text, body, status, position):
    for players in server.jugadoresConectados:
        address = players.address
        serverResponse(address, text, body, status, position)
# Enviar un response a todos los jugadores conectados EXCEPTO a un jugador elegido
def serverResponseGlobalExcept(server, excepted, text, body, status, position):
    for index, players in enumerate(server.jugadoresConectados):
        if index != excepted:
            address = players.address
            serverResponse(address, text, body, status, position)
#  Calcula el orden ciclico de turnos
def turnCalculate(turnCount, server):
    turnCount += 1
    if(turnCount > len(server.jugadoresConectados)):
        turnCount = 1
    # Salta los turnos de jugadores perdedores
    while(server.jugadoresConectados[turnCount-1].vidas == 0):
        turnCount += 1
        if(turnCount > len(server.jugadoresConectados)):
            turnCount = 1
    return turnCount

def receiveMessage(UDPServerSocket, bufferSize):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    return bytesAddressPair[0], bytesAddressPair[1]

def battleMatch(server):
    matchOngoing = True
    turnCount = 1
    while(matchOngoing):
        # Avisa y maneja los turnos
        print("Turno jugador: {}".format(turnCount))
        addressInTurn = server.jugadoresConectados[turnCount-1].address
        serverResponse(addressInTurn, "Es tu turno", "s", 1, [])
        serverResponseGlobalExcept(server, turnCount-1, "Es el turno del jugador {}".format(turnCount), "s", 0, [])

        # Recibir acciones de participantes
        message, address = receiveMessage(UDPServerSocket, bufferSize)

        # Verifica si es el address del jugador en turno
        if(address == addressInTurn):
            # Decodifica el mensaje JSON
            receivedJson = json.loads(message.decode())
            clientMsg = (receivedJson["action"],receivedJson["position"])
            print(clientMsg)
            # Actualiza la informacion de la partida
            attackPos = receivedJson["position"]
            print(attackPos[0])
            print(attackPos[1])
            for index, player in enumerate(server.jugadoresConectados):
                if index != (turnCount-1):
                    player.recibirAtaque(BattleClasses.Coordenada(attackPos[0], attackPos[1]))

            # Avisa la accion a todos los jugadores
            serverResponse(addressInTurn, "Atacaste en la posicion: {}".format(receivedJson["position"]), "a", 1, receivedJson["position"])
            serverResponseGlobalExcept(server, turnCount-1,
                                       "El jugador {} ataco la posicion {}!".format(turnCount, receivedJson["position"]),
                                       "a", 1, receivedJson["position"])
            # Mantiene un orden ciclico de turnos
            turnCount = turnCalculate(turnCount, server)



# Listen for incoming datagrams
while(True):
    message, address = receiveMessage(UDPServerSocket, bufferSize)

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
        server.printParticipants()
        
    # Verifica si se inicio la partida
    elif (clientMsg == "s"):
        # Confirmacion de inicio de partida
        print("Un jugador dio la orden de empezar una partida")
        serverResponseGlobal(server, "Se empezo la partida!",clientMsg, 1, [])

        # Quienes estan participando de la partida en el server
        print("JUGADORES PARTICIPANTES:")
        server.printParticipants()

        # iniciar partida
        server.iniciarPartida # aun no hace nada xd
        # while de partida en curso
        battleMatch(server)

    else:
        # Comando erroneo
        print("Denegacion de comando entrante")
        serverResponse(address, "Comando erroneo, intente denuevo", clientMsg, 0, [])