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
               self.estado = "destruido"

    def hundir(self):
        self.estado = "hundido"

class Casilla:
    def __init__(self):
        self.barco = None
        self.estado = "vacío"

    def agregarBarco(self, barco: Barco):
        self.barco = barco
        self.estado = "ocupado"

    def atacarCasilla(self):
        print(self.barco, self.estado)
        if (self.estado == "ocupado"):
            if (self.barco.estado == "operativo"):
                self.estado = "dañado"
                self.barco.recibirDaño()
                print("acerto!!\n")
                return True
        return False

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

    def realizarAtaque(self, coordenada: Coordenada):
        return self.casillas[coordenada.x-1][coordenada.y-1].atacarCasilla()

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

    def iniciarPartida(self):
        # Implementar lógica para emparejar jugadores e iniciar una partida
        pass

    def finalizarPartida(self):
        # Lógica para terminar una partida y anunciar el resultado
        pass

class Cliente:
    def __init__(self, nombre: str, servidor: Servidor):
        self.nombre = nombre
        self.servidor = servidor
        self.jugador = Jugador(nombre)

    def conectarAServidor(self):
        self.servidor.conectarJugador(self.jugador)

    def desconectar(self):
        # Implementar lógica para desconexión
        pass

    def jugarTurno(self, coordenada: Coordenada):
        resultado = self.jugador.recibirAtaque(coordenada)
        # Enviar resultado al servidor y recibir actualizaciones
        pass

