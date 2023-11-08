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
print("Digite o IP do servidor: ", end="")
ip = input()

server_address = (ip, 5968)

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

        # Imprime dados recebidos
        print(f"Número de sequência: {new_sequence_number}")
        print(f"Temperatura: {temperature}°C")

        temperature_sum += temperature
        packages_received += 1

        # Se é o primeiro pacote recebido, não faz a verificação do número de sequência
        if old_sequence_number == -1:
            old_sequence_number = new_sequence_number
            continue

        # Caso contrário, verifica se o número de sequência é diferente do esperado
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
        # Se o cliente digitar "unsubscribe", envia pedido de cancelamento da inscrição para o servidor
        if str == 'unsubscribe' or str == 'u' or str == 'exit' or str == 'e' or str == 'quit' or str == 'q':
            socket.sendto(b"unsubscribe", server_address)
            stop_thread.set()
            socket.close()
            break

# Thread para ler input do teclado
input_thread = threading.Thread(target=get_input)
input_thread.start()

receive_thread.join()

print("\nRelatório:\n")
print(f"Número total de pacotes recebidos: {packages_received}")
print(f"Número total de pacotes perdidos: {packages_lost}")
print(f"Número total de pacotes recebidos fora de ordem: {packages_out_of_order}\n")
print(f"Soma das temperaturas recebidas: {temperature_sum}")
print(f"Média da temperatura: {temperature_sum / packages_received}°C")