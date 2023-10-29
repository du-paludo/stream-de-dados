import socket
import struct

# Cria um socket UDP
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Endereço e porta do servidor
server_address = ("192.168.0.8", 5968)

# Faz pedido de subscrição
socket.sendto(b"subscribe", server_address)

while True:
    # Recebe dados do servidor
    data, server = socket.recvfrom(1024)

    # Extrai número de sequência e temperatura
    # sequence_number = int.from_bytes(data[:4], byteorder='big')
    # temperature = int.from_bytes(data[4:], byteorder='big')

    sequence_number, temperature = struct.unpack('!If', data)

    # Imprime dados recebidos
    print(f"Sequence number: {sequence_number}")
    print(f"Temperature: {temperature}°C")

# Fecha o socket
socket.close()