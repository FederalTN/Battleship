import threading
import socket

# Función para el servidor UDP
def servidor_udp():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind(('127.0.0.1', 12345))

    while True:
        datos, direccion = servidor.recvfrom(1024)
        print(f'Servidor UDP recibió: {datos.decode()} desde {direccion}')

# Función para el cliente UDP
def cliente_udp():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    i=0
    while True:
        mensaje = str(i)
        cliente.sendto(mensaje.encode(), ('127.0.0.1', 12345))
        i +=1

# Crea un hilo para el servidor UDP
hilo_servidor = threading.Thread(target=servidor_udp)

# Inicia el hilo del servidor UDP
hilo_servidor.start()

# Crea un hilo para el cliente UDP
hilo_cliente = threading.Thread(target=cliente_udp)

# Inicia el hilo del cliente UDP
hilo_cliente.start()

# Espera a que los hilos terminen
hilo_servidor.join()
hilo_cliente.join()
