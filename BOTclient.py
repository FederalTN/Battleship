import socket
import json
import sys
import BattleClasses
import validations
import time
import random

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

with open('config.json', 'r') as archivo_config:
    configuracion = json.load(archivo_config)

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
    #print(msg)
    return receivedJson
# Genera una combinacion de barcos para el bot aleatoriamente
def randomShips(dimension: int):
    # Definir los posibles valores para el tablero
    z_values = [0, 1]                       
    # Crear una lista de barcos
    ships = {
        "p": [],
        "b": [],
        "s": []
    }
    i=0
    # Generar combinaciones aleatorias para cada barco
    for ship_type, ship_positions in ships.items():
        # Definir los posibles valores para el tablero POR barco
        x_values = list(range(1, dimension+1-i))
        y_values = list(range(1, dimension+1-i))

        x = random.choice(x_values)
        y = random.choice(y_values)
        z = random.choice(z_values)

        i += 1
        ship_positions.extend([x, y, z])
    return ships
# Ataque random
def randomAttack(posList):
    # Genera un índice aleatorio dentro del rango válido
    indice_aleatorio = random.randint(0, len(posList) - 1)

    # Obtiene la posicion para atacar y la elimina de la lista de ataques posibles
    pos = posList.pop(indice_aleatorio)
    return pos
# Lista de reserva de posiciones posibles, utilizado para que el bot no repita ataques inutiles
def initializePossibleAttackpos(dimension: int):
    posList = []
    for y in range(1, dimension+1):
        for x in range(1, dimension+1):
            posList.append([x,y])
    return posList


def BOT():
    # DIMENSIONES TABLERO
    dimension = configuracion["dimension"]
    alt = configuracion["compatibilidad"]
    posList = initializePossibleAttackpos(dimension)
    # accion para la conexion
    sendAction("c", "", "", "")
    receivedJson = receiveRespond()

    # Comprueba si se realiza una conexion
    connected = False
    if((receivedJson["action"],receivedJson["status"]) == ("c",1)): connected = True
    while(connected):
            receivedJson = receiveRespond()

            onMatch = True
            while(onMatch):
                # Recibir confirmacion de turnos
                receivedJson = receiveRespond()
                # Si es tu turno puedes hacer acciones
                if(receivedJson["status"] == 1):
                    if(receivedJson["action"] == "t"):
                        coordenadas = randomAttack(posList)
                        sendAction("a", "", "", [coordenadas[0] -alt, coordenadas[1] -alt])
                        # Confirmacion de accion propia
                        receivedJson = receiveRespond()            
                    elif(receivedJson["action"] == "b"):
                        while True:
                            ships = randomShips(dimension)
                            if (validations.shipOverlaps(ships) or validations.shipPosOutBoundsValidation(ships)): pass
                            else:
                                for key, value in ships.items():
                                    ships[key][:2] = [x - alt for x in value[:2]]
                                break
                        sendAction("b", "", ships, [])
                        # Confirmacion de construccion propia
                        receivedJson = receiveRespond()
                    # Verifica si ganaste derrotando al rival
                    elif(receivedJson["action"] == "w"):
                        print("\nGANASTE!!!!!!")
                        onMatch = False
                        connected = False
                    # Verifica si perdiste por tener 0 vidas
                    elif(receivedJson["action"] == "l"):
                        print("\nPERDISTE!!!!!!")
                        onMatch = False
                        connected = False
                # Si no es tu turno debes esperar a que lo sea
                else:
                    # Esperar confirmacion de accion de otro jugador
                    receivedJson = receiveRespond()
                    # Verifica si ganaste por desconexion del rival
                    if(receivedJson["action"] == "w"):
                        print("\nGANASTE!!!!!!")
                        onMatch = False
                        connected = False

