import json

# DIMENSIONES TABLERO
with open('config.json', 'r') as archivo_config:
    configuracion = json.load(archivo_config)
dimension = configuracion["dimension"]

# VERIFICAR si dos barcos se sobrelapan
def shipOverlapValidation(ships, index1: int, index2: int):
    ship1 = list(ships.keys())[index1]
    ship2 = list(ships.keys())[index2]

    #print(ship1, ships[ship1], ship2 , ships[ship2])
    x1 , y1, orientation1 = ships[ship1]
    _ , _, orientation2 = ships[ship2]
    z1 = 1 if ship1 == "p" else (2 if ship1 == "b" else 3)
    z2 = 1 if ship2 == "p" else (2 if ship2 == "b" else 3)

    for _ in range(z1):
        x2 , y2, _ = ships[ship2]
        for _ in range(z2):
            #print(x1, y1, x2, y2)
            #Valida si hay un overlap con el otro barco o con los bordes del tablero
            if (x1, y1) == (x2, y2) or x1 > dimension or y1 > dimension or x1 < 1 or y1 < 1 or x2 > dimension or y2 > dimension or x2 < 1 or y2 < 1: return True
            if orientation2 == 0:  # Vertical
                y2 += 1
            else:
                x2 += 1
        if orientation1 == 0:  # Vertical
            y1 += 1
        else:
            x1 += 1
    return False
def shipOverlaps(ships):
    return shipOverlapValidation(ships, 0, 1) or shipOverlapValidation(ships, 0, 2) or shipOverlapValidation(ships, 1, 2)

def shipPosOutBoundsValidation(ships: dict):
    for clave, valores in ships.items():
        for valor in valores:
            if (valor < 1) or (valor > dimension):
                return True
    return False

def AttackCoordsValidation(pos: list):
    if ((pos[0] < 1) or (pos[0] > dimension)) or ((pos[1] < 1) or (pos[1] > dimension)): return False
    return True

