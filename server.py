import socket
import json
import sys
import BattleClasses
import validations
import threading
import BOTclient

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

server = BattleClasses.Servidor()

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

with open('config.json', 'r') as archivo_config:
    configuracion = json.load(archivo_config)

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
# Calcula el orden ciclico de turnos
def turnCalculate(turnCount, server):
    turnCount += 1
    if(turnCount > len(server.jugadoresConectados)):
        turnCount = 1
    # Salta los turnos de jugadores perdedores
    while(server.jugadoresConectados[turnCount-1].vidas < 1):
        turnCount += 1
        if(turnCount > len(server.jugadoresConectados)):
            turnCount = 1
    return turnCount
# Recibir un mensaje en el socket UDP
def receiveMessage(UDPServerSocket, bufferSize):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    return bytesAddressPair[0], bytesAddressPair[1]

# Se maneja la batalla de barcos
def battleMatch(server):
    matchOngoing = True
    turnCount = 1

    for players in server.jugadoresConectados:
        serverResponse(players.address, "CONSTRUYE TUS BARCOS\n", "b", 1, [])
        message, address = receiveMessage(UDPServerSocket, bufferSize)
        receivedJson = json.loads(message.decode())
        # VALIDA la construccion de los barcos
        if (validations.shipOverlaps(receivedJson["ships"]) or validations.shipPosOutBoundsValidation(receivedJson["ships"])):
            serverResponse(address, "ERROR", "d", 0, [])
            break
        else:
            for battleship in receivedJson["ships"]:
                shipData = [int(ship) for ship in receivedJson["ships"][battleship]]
                horizontalidad = True if shipData[2] == 1 else False
                players.tablero.colocarBarco(BattleClasses.Barco(battleship), BattleClasses.Coordenada(shipData[0], shipData[1]), horizontalidad)
            serverResponse(address, "Construido con exito", "b", 1, [])
            

    DestroyedPlayer = False
    while(matchOngoing):
        alt = configuracion["compatibilidad"]
        # Avisa y maneja los turnos
        print("Turno jugador: {}".format(turnCount))
        addressInTurn = server.jugadoresConectados[turnCount-1].address
        serverResponse(addressInTurn, "Es tu turno\n", "t", 1, [])
        serverResponseGlobalExcept(server, turnCount-1, "Es el turno del jugador {}\n".format(turnCount), "t", 0, [])

        # Recibir acciones de participantes
        try:
            message, address = receiveMessage(UDPServerSocket, bufferSize)
        except Exception as e:
            serverResponse(address, "ERROR\n", "d", 1, [])
        # Verifica si es el address del jugador en turno
        if(address == addressInTurn):
            # Decodifica el mensaje JSON
            receivedJson = json.loads(message.decode())
            clientMsg = (receivedJson["action"],receivedJson["position"])
            print(clientMsg)

            if (receivedJson["action"] == "d"):
                for index, player in enumerate(server.jugadoresConectados):
                        if index != (turnCount-1):
                            serverResponse(player.address, "Ganaste por desconexion del rival", "w", 1, "")
                        else:
                            serverResponse(addressInTurn, "Desconectaste del servidor", "d", 1, "")
                break
            elif (receivedJson["action"] == "a"):
                # Actualiza la informacion de la partida en un ataque
                attackPos = receivedJson["position"]
                # Valida si el ataque es correcto
                if not (validations.AttackCoordsValidation(attackPos)):
                    serverResponse(address, "ERROR", "a", 0, [])
                    break
                hit = False # Variable booleana que comprueba si el atacante logro un acierto
                for index, player in enumerate(server.jugadoresConectados):
                    if index != (turnCount-1):
                        # Envia el ataque a los players y avisa si les dio
                        hurt = player.recibirAtaque(BattleClasses.Coordenada(attackPos[0], attackPos[1]))
                        if (hit == False) & (hurt): hit = True
                        if hurt:
                            serverResponse(player.address, "El jugador {} ataco la posicion {}, Y TE DIO!".format(turnCount, receivedJson["position"]),
                                            "a", 1, receivedJson["position"])
                            if (player.vidas == 0):
                                serverResponse(player.address, "Te quedaste sin vidas y perdiste...", "l", 1, "")
                                serverResponse(addressInTurn, "Atacaste en la posicion: {} y GANASTE".format(receivedJson["position"]),
                                                 "a", 1, receivedJson["position"])
                                serverResponse(addressInTurn, "Ganaste destruyendo a tu rival!", "w", 1, "")
                                DestroyedPlayer = True
                        else:
                            serverResponse(player.address, "El jugador {} ataco la posicion {}, no te dio".format(turnCount, receivedJson["position"]),
                                            "a", 0, receivedJson["position"])
                if DestroyedPlayer: break
                # Confirmacion para el atacante
                if hit: 
                    serverResponse(addressInTurn, "Atacaste en la posicion: {} y ACERTASTE".format(receivedJson["position"]),
                                    "a", 1, receivedJson["position"])
                else:
                    serverResponse(addressInTurn, "Atacaste en la posicion: {} y fallaste".format(receivedJson["position"]),
                                    "a", 0, receivedJson["position"])                
                # Mantiene un orden ciclico de turnos
                turnCount = turnCalculate(turnCount, server)
            else:
                serverResponse(addressInTurn, "ERROR: COMANDO ERRONEO\n", "d", 1, [])
            


goStart = 0 # Contador de jugadores pidiendo partida
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

        # Partida PvP
        if (receivedJson["bot"] == 0):
            goStart += 1
            if (goStart > 1):
                serverResponseGlobal(server, "Se empezo la partida! espera tu turno!", clientMsg, 1, [])

                # Quienes estan participando de la partida en el server
                print("JUGADORES PARTICIPANTES:")
                server.printParticipants()

                # while de partida en curso
                battleMatch(server)
                # Actualizacion cuando termine la partida
                for i in range(len(server.jugadoresConectados)):
                    server.jugadoresConectados[i].refrescarJugador()
                goStart = 0
        # Partida PvE (BOT)
        else:
            def serverPvE():
                if(len(server.jugadoresConectados) < 2):
                    message, address = receiveMessage(UDPServerSocket, bufferSize)
                    receivedJson = json.loads(message.decode())

                    server.conectarJugador(BattleClasses.Jugador("Client BOT", address))
                    serverResponse(address, "", "c", 1, [])

                serverResponseGlobal(server, "Se empezo la partida! espera tu turno!", clientMsg, 1, [])

                print("JUGADORES PARTICIPANTES:")
                server.printParticipants()

                # while de partida en curso
                battleMatch(server)

            serverThread = threading.Thread(target=serverPvE)
            serverThread.start()
            botThread = threading.Thread(target=BOTclient.BOT)
            botThread.start()

            # Espera a que los hilos terminen
            serverThread.join()
            botThread.join()

            
            # Actualizacion cuando termine la partida
            server.jugadoresConectados[1].refrescarJugador()
            server.jugadoresConectados.pop(1)
            server.jugadoresConectados[0].refrescarJugador()
               

            

##########################################################
            
    else:
        # Comando de cliente erroneo
        print("Denegacion de comando entrante")
        serverResponse(address, "Comando erroneo, intente denuevo", clientMsg, 0, [])