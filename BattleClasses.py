from typing import List, Tuple
import json

# DIMENSIONES TABLERO
with open('config.json', 'r') as archivo_config:
    configuracion = json.load(archivo_config)
dimension = configuracion["dimension"]

class Coordenada:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Barco:
    def __init__(self, tipo: str):
        self.tipo = tipo
        self.blindaje = 0
        self.estado = "operativo"
        
    def recibirDaño(self):
        if (self.estado == "operativo"):
            self.blindaje -= 1
            if (self.blindaje == 0):
               print(self.tipo, "destruido!")
               self.estado = "hundido"

class Casilla:
    def __init__(self):
        self.barco = None
        self.estado = "vacío"

    def agregarBarco(self, barco: Barco):
        self.barco = barco
        self.estado = "ocupado"
    #Solo en el servidor: actualiza los mapas de los jugadores si reciben un ataque
    def atacarCasilla(self):
        print(self.barco, self.estado)
        if (self.estado == "ocupado"):
            if (self.barco.estado == "operativo"):
                self.estado = "dañado"
                self.barco.recibirDaño()
                print("acerto!!\n")
                return True
        return False
    #Solo en el cliente: actualiza el mapa si el ataque acerto a un enemigo
    def atacarCasillaEnemigo(self, status: bool):
        if status:
            self.estado = "Acierto"
            print("acertadoo")
        else:
            if (self.estado != "Acierto"):
                self.estado = "Pifia"
                print("pifiadooo")
    
    def __str__(self):
       # Devuelve una representación en forma de cadena del estado de la casilla
        if self.estado == "vacío":
            return "O"
        elif self.estado == "Pifia":
            return "X"
        elif self.estado == "Acierto":
            return "A"


class Tablero:
    def __init__(self):
        self.casillas = [[Casilla() for _ in range(dimension)] for _ in range(dimension)]

    def colocarBarco(self, barco: Barco, coord: Coordenada, horizontal: bool):
        if(barco.tipo == "p"): espacios = 1
        elif(barco.tipo == "b"): espacios = 2
        else: espacios = 3
        for i in range(espacios):
            print((coord.x, coord.y))
            self.casillas[coord.x-1][coord.y-1].agregarBarco(barco)
            barco.blindaje += 1
            if(horizontal):
                coord.x += 1
            else:
                coord.y += 1

    #Solo en el servidor: actualiza los mapas de los jugadores si reciben un ataque.
    def realizarAtaque(self, coordenada: Coordenada):
        return self.casillas[coordenada.x-1][coordenada.y-1].atacarCasilla()
    #Solo en el cliente: actualiza el mapa si el ataque acerto a un enemigo.
    def realizarAtaqueEnEnemigo(self, coordenada: Coordenada, status: bool):
        return self.casillas[coordenada.x-1][coordenada.y-1].atacarCasillaEnemigo(status)
    #Solo en el cliente: Implementa un mapa para ver la partida en curso.
    def ImprimirTablero(self):
        for i in range(dimension):
            for j in range(dimension):
                # Imprimir las casillas en orden inverso por la diagonal
                casilla = self.casillas[j][i]
                print(casilla, end=' ')
            print()

class Jugador:
    def __init__(self, nombre: str, address):
        self.nombre = nombre
        self.address = address
        self.tablero = Tablero()
        self.vidas = 6

    def refrescarJugador(self):
        print("JUGADOR ACTUALIZADO")
        self.tablero = Tablero()
        self.vidas = 6

    def recibirAtaque(self, coordenada: Coordenada):
        acertado = self.tablero.realizarAtaque(coordenada)
        if acertado: self.vidas -= 1
        return acertado

class Servidor:
    def __init__(self):
        self.jugadoresConectados = []

    def conectarJugador(self, jugador: Jugador):
        self.jugadoresConectados.append(jugador)
        print(("Conectado el jugador: {}".format(jugador.nombre)))

    def printParticipants(self):
        listaPlayers = self.jugadoresConectados
        for players in listaPlayers:
            print(players.nombre)
        print("")

class Cliente:
    def __init__(self):
        self.tableroEnemigo = Tablero()

    def refrescarEnemigo(self):
        self.tableroEnemigo = Tablero()
    
