import socket
import json
import sys
import BattleClasses
import validations

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

# xd client = BattleClasses.Cliente("Federal", localPort)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Envio de mensajes
def sendAction(body, type, fleet, pos: list):
    msgFromClient = {
        "action": body, # connection, attack, lose, build, disconnect, select
        "bot": type, # 0 o 1, 1: partida vs bot, 0: partida vs otro cliente
        "ships": fleet, # cordenada (x,y) y orientación (0: vertical, 1: horizontal)
        "position": pos, # posicion de ataque
    }
    bytesToSend = json.dumps(msgFromClient).encode()
    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, (localIP, localPort))
# Recibir respuestas del server
def receiveRespond():
    # Recibe respuesta
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    # Decodifica el mensaje JSON
    receivedJson = json.loads(msgFromServer[0].decode())
    msg = "Message from Server: {}".format(receivedJson["response"])
    print(msg)
    return receivedJson

# accion para la conexion
sendAction("c", "", "", "")
receivedJson = receiveRespond()

# Comprueba si se realiza una conexion
connected = False
if((receivedJson["action"],receivedJson["status"]) == ("c",1)): connected = True
while(connected):

    inputString = input("\nJUGAR CONTRA UN JUGADOR?(S/n): ")
    
    if(inputString == "S" or inputString == "s"):
        sendAction("s", 0, "", [])
        print("Esperando a que conecte otro jugador...")
        receivedJson = receiveRespond()
    elif(inputString == "N" or inputString == "n"):
        sendAction("s", 1, "", [])
        receivedJson = receiveRespond()
        print("Partida VS bot")


    onMatch = True
    while(onMatch):
        # Recibir confirmacion de turnos
        print("Recibiendo orden de turno...")
        receivedJson = receiveRespond()
        # Si es tu turno puedes hacer acciones
        if(receivedJson["status"] == 1):
            if(receivedJson["action"] == "t"):
                while True:
                    inputString = input("\nDONDE ATACAS? X Y: ")

                    # Avisar al servidor de que te desconectaras (En vez de atacar)
                    if(inputString == "D" or inputString == "d"):
                        sendAction("d", 0, "", [])
                        print("Esperando a que conecte otro jugador...")
                        receivedJson = receiveRespond()
                        onMatch = False
                        break
                    else:
                        try:
                            coordenadas = inputString.split()
                            coordenadas = [int(x) for x in coordenadas]
                            if (validations.AttackCoordsValidation(coordenadas)):
                                sendAction("a", "", "", [int(coordenadas[0]), int(coordenadas[1])])
                                # Confirmacion de accion propia
                                receivedJson = receiveRespond()
                                break
                            else:
                                print("Coordenadas de ataque invalida")
                        except Exception as e:
                            print("ERROR, introduzca nuevamente un comando valido (ataque o disconnect)", e)
            
            elif(receivedJson["action"] == "b"):
                while True:
                    inputPatrol = input("\nDONDE ESTARA EL BARCO PATRULLA? X Y ORIENTATION: ")
                    inputBattleship = input("\nDONDE ESTARA EL BARCO ACORAZADO? X Y ORIENTATION: ")
                    inputSubmarine = input("\nDONDE ESTARA EL SUBMARINO? X Y ORIENTATION: ")

                    buildOrderP = inputPatrol.split()
                    buildOrderB = inputBattleship.split()
                    buildOrderS = inputSubmarine.split()

                    ships = {
                        "p": [int(buildOrderP[0]), int(buildOrderP[1]), int(buildOrderP[2])],
                        "b": [int(buildOrderB[0]), int(buildOrderB[1]), int(buildOrderB[2])],
                        "s": [int(buildOrderS[0]), int(buildOrderS[1]), int(buildOrderS[2])]
                    }

                    if (validations.shipOverlaps(ships) or validations.shipPosOutBoundsValidation(ships)):
                        print("Coordenadas erronea de barcos, introduce las coordenadas nuevamente.")
                    else:
                        break
                sendAction("b", "", ships, [])
                # Confirmacion de construccion propia
                receivedJson = receiveRespond()
            # Verifica si ganaste derrotando al rival
            elif(receivedJson["action"] == "w"):
                print("\nGANASTE!!!!!!")
                onMatch = False

            # Verifica si perdiste por tener 0 vidas
            elif(receivedJson["action"] == "l"):
                print("\nPERDISTE!!!!!!")
                onMatch = False

        # Si no es tu turno debes esperar a que lo sea
        else:
            # Esperar confirmacion de accion de otro jugador
            receivedJson = receiveRespond()
            # Verifica si ganaste por desconexion del rival
            if(receivedJson["action"] == "w"):
                print("\nGANASTE!!!!!!")
                onMatch = False

    


