import socket
import struct
import threading

# Estatísticas UDP
packages_received = 0
packages_lost = 0
packages_out_of_order = 0
old_sequence_number = -1

# Estatística temperatura
temperature_sum = 0

# Cria um socket UDP
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Endereço e porta do servidor
server_address = ("192.168.0.8", 5968)

# Faz pedido de subscrição
socket.sendto(b"subscribe", server_address)

stop_thread = threading.Event()
def receive_data():
    global packages_received 
    global packages_lost
    global packages_out_of_order
    global old_sequence_number
    global temperature_sum

    while not stop_thread.is_set():
        # Recebe dados do servidor
        try:
            data, server = socket.recvfrom(1024)
        except:
            break

        # Extrai número de sequência e temperatura
        new_sequence_number, temperature = struct.unpack('!If', data)
        # sequence_number = int.from_bytes(data[:4], byteorder='big')
        # temperature = int.from_bytes(data[4:], byteorder='big')

        # Imprime dados recebidos
        print(f"Sequence number: {new_sequence_number}")
        print(f"Temperature: {temperature}°C")

        temperature_sum += temperature
        packages_received += 1

        if old_sequence_number == -1:
            old_sequence_number = new_sequence_number
            continue

        if new_sequence_number < old_sequence_number:
            packages_out_of_order += 1
        elif new_sequence_number > old_sequence_number + 1:
            packages_lost += new_sequence_number - old_sequence_number - 1
        old_sequence_number = new_sequence_number

# Thread para receber os dados
receive_thread = threading.Thread(target=receive_data)
receive_thread.daemon = True
receive_thread.start()

def get_input():
    while not stop_thread.is_set():
        str = input()
        if str == 'unsubscribe' or str == 'u' or str == 'exit' or str == 'e' or str == 'quit' or str == 'q':
            socket.sendto(b"unsubscribe", server_address)
            stop_thread.set()
            socket.close()
            break

# Thread para ler input do teclado
input_thread = threading.Thread(target=get_input)
input_thread.start()

receive_thread.join()

print("Report:")
print(f"Total number of packages received: {packages_received}")
print(f"Total number of packages lost: {packages_lost}")
print(f"Total number of packages out of order: {packages_out_of_order}")
print("")
print(f"Sum of received temperatures: {temperature_sum}")
print(f"Average temperature: {temperature_sum / packages_received}°C")