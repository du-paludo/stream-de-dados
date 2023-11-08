import socket
import requests
import threading
import struct
from time import sleep

# Dados da API
api_url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": -25.4284,
    "longitude": -49.2733,
    "current": "temperature_2m",
    "timezone": "auto",
    "forecast_days": 1
}
interval = 2
sequence_number = 0
total_clients_connected = 0

# Socket UDP para enviar dados
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Socket UDP para receber pedidos de subscrição
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Porta do servidor
server_address = ("", 5968)

# Conecta o socket de recebimento ao endereço do servidor
receive_socket.bind(server_address)
print("Servidor UDP ativo e escutando na porta 5968.")

# Dicionário de clientes subscritos
subscribed_clients = {}

# Variável para parar as threads
stop_thread = threading.Event()

# Função para enviar temperatura
def send_temperature():
    global interval
    global sequence_number

    while not stop_thread.is_set():
        response = requests.get(api_url, params=params)
        sequence_number += 1

        # Checa se a chamada da API foi bem-sucedida (status code 200)
        if response.status_code == 200:
            data = response.json()
            temperature = data["current"]["temperature_2m"]
            print(f"Temperatura em Curitiba: {temperature}°C")
        else:
            print(f"Falha ao receber os dados. Código: {response.status_code}")

        # Converte a temperatura (float) para 4 bytes
        temperature_bytes = struct.pack('!f', temperature)  # 'f' representa um float de 32 bits

        # Converte o número de sequência (um inteiro) para 4 bytes
        sequence_number_bytes = struct.pack('!I', sequence_number) # 'I' representa um inteiro sem sinal de 32 bits
        
        # Monta um pacote com as duas informações
        package = sequence_number_bytes + temperature_bytes

        # Envia o pacote para cada cliente na lista de clientes inscritos
        for client_address in subscribed_clients:
            try:
                send_socket.sendto(package, client_address)
            except:
                break

        # Aguarda o tempo determinado antes de enviar novamente
        sleep(interval)

# Thread para enviar dados
send_thread = threading.Thread(target=send_temperature)
send_thread.daemon = True
send_thread.start()

# Função para receber pedidos de subscrição
def receive_requests():
    global total_clients_connected

    while not stop_thread.is_set():
        try:
            # Recebe mensagens
            data, client_address = receive_socket.recvfrom(1024)
        except:
            break

        # Se a mensagem for um pedido de inscrição, adiciona o cliente na lista de clientes inscritos
        if data == b"subscribe":
            subscribed_clients[client_address] = True
            total_clients_connected += 1
            print(f"Cliente {client_address} registrou-se na lista de transmissão do servidor.")
        # Se a mensagem for um pedido de cancelamento de inscrição, remove o cliente da lista de clientes inscritos
        elif data == b"unsubscribe":
            send_socket.sendto(b"close", client_address)
            subscribed_clients.pop(client_address, None)
            print(f"Cliente {client_address} cancelou sua inscrição na lista de transmissão do servidor.")

# Thread para receber pedidos de subscrição
receive_thread = threading.Thread(target=receive_requests)
receive_thread.daemon = True
receive_thread.start()

def get_input():
    global interval
    global send_socket
    global receive_socket
    
    while not stop_thread.is_set():
        str = input()

        # Se o input for "setinterval", altera o intervalo de envio para o tempo especificado
        if str.startswith("setinterval"):
            interval = float(str.split(" ")[1])
            print("Intervalo de envio alterado para " + str.split(" ")[1] + " segundos.")
        # Se o input for "exit", encerra o programa
        if str == 'exit' or str == 'e' or str == 'quit' or str == 'q':
            stop_thread.set()
            send_socket.close()
            receive_socket.close()
            break

# Thread para ler input do teclado
input_thread = threading.Thread(target=get_input)
input_thread.daemon = True
input_thread.start()

# Mantém o programa rodando
send_thread.join()

# Imprime relatório final
print("\nRelatório:\n")
print(f"Número total de pacotes enviados: {sequence_number}")
print(f"Número total de clientes conectados: {total_clients_connected}")
print(f"Número de clientes conectados ao encerrar: {len(subscribed_clients)}")