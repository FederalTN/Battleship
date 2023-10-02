import socket
import json
import sys
import BattleClasses

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

# xd client = BattleClasses.Cliente("Federal", localPort)

# barcos del cliente
fleet = {
    "p": [1,1,0], # cordenada (x,y) y orientación (0: vertical, 1: horizontal)
    "b": [1,2,1],
    "s": [2,3,0]
}
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

    inputString = input("\nESPERAR MAS JUGADORES O QUIERES INICIAR LA PARTIDA?(S/n): ")
    
    if(inputString == "S" or inputString == "s"):
        sendAction("s", "", "", "")
        receivedJson = receiveRespond()
    elif(inputString == "N" or inputString == "n"):
        print("Esperando a que inicien la partida...")
        receivedJson = receiveRespond()

    onMatch = True
    while(onMatch):
        # Recibir confirmacion de turnos
        receivedJson = receiveRespond()
        # Si es tu turno puedes hacer acciones
        if(receivedJson["status"] == 1):
            inputString = input("\nDONDE ATACAS?: ")
            coordenadas = inputString.split()
            sendAction("a", "", "", [int(coordenadas[0]), int(coordenadas[1])])
            # Confirmacion de accion propia
            receivedJson = receiveRespond()
        # Si no es tu turno debes esperar a que lo sea
        else:
            # Esperar confirmacion de accion de otro jugador
            receivedJson = receiveRespond()
    


