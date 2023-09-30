from typing import List, Tuple

class Coordenada:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Barco:
    def __init__(self, tipo: str):
        self.tipo = tipo
        self.estado = "intacto"
        
    def recibirAtaque(self):
        if self.estado == "intacto":
            self.estado = "dañado"
            
    def hundir(self):
        self.estado = "hundido"

class Casilla:
    def __init__(self):
        self.estado = "vacío"
        self.barco = None

    def agregarBarco(self, barco: Barco):
        self.barco = barco
        self.estado = "ocupado"

    def atacarCasilla(self):
        if self.estado == "ocupado" and self.barco:
            self.barco.recibirAtaque()
            return True
        return False

class Tablero:
    def __init__(self, dimension: int = 20):
        self.casillas = [[Casilla() for _ in range(dimension)] for _ in range(dimension)]

    def colocarBarco(self, barco: Barco, coordenadas: List[Coordenada]):
        for coord in coordenadas:
            self.casillas[coord.x][coord.y].agregarBarco(barco)

    def realizarAtaque(self, coordenada: Coordenada):
        return self.casillas[coordenada.x][coordenada.y].atacarCasilla()

class Jugador:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.tablero = Tablero()
        self.vidas = 6

    def realizarAccion(self, coordenada: Coordenada):
        return self.tablero.realizarAtaque(coordenada)

class Servidor:
    def __init__(self):
        self.jugadoresConectados = []

    def conectarJugador(self, jugador: Jugador):
        self.jugadoresConectados.append(jugador)
        print(("Conectado el jugador: {}".format(jugador.nombre)))

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
        resultado = self.jugador.realizarAccion(coordenada)
        # Enviar resultado al servidor y recibir actualizaciones
        pass

