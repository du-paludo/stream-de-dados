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
interval = 10

# Socket UDP para enviar dados
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Socket UDP para receber pedidos de subscrição
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Porta do servidor
server_address = ("", 5968)

# Conecta o socket de recebimento ao endereço do servidor
receive_socket.bind(server_address)
print("UDP server up and listening")

# Dicionário de clientes subscritos
subscribed_clients = {}

# Função para enviar temperatura
def send_temperature():
    global interval
    sequence_number = -1
    while True:
        response = requests.get(api_url, params=params)
        sequence_number += 1
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
        
            # Now you can access the data
            temperature = data["current"]["temperature_2m"]
        
            # Print the temperature
            print(f"Temperature at 2 meters above ground: {temperature}°C")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

        # 32 bits para número de sequência
        # 32 bits para temperatura (float)

        # Convert temperature (a float) to 4 bytes
        temperature_bytes = struct.pack('!f', temperature)  # 'f' represents a 32-bit float

        # Convert sequence_number (an integer) to 4 bytes
        sequence_number_bytes = struct.pack('!I', sequence_number)  # 'I' represents a 32-bit unsigned integer
        package = sequence_number_bytes + temperature_bytes
        for client_address in subscribed_clients:
            send_socket.sendto(package, client_address)

        sleep(interval)

# Thread para enviar dados
send_thread = threading.Thread(target=send_temperature)
send_thread.daemon = True
send_thread.start()

# Função para receber pedidos de subscrição
def receive_requests():
     while True:
        data, client_address = receive_socket.recvfrom(1024)  # Adjust buffer size as needed

        if data == b"subscribe":
            subscribed_clients[client_address] = True
            print(f"Client {client_address} has subscribed.")
        elif data == b"unsubscribe":
            subscribed_clients.pop(client_address, None)
            print(f"Client {client_address} has unsubscribed.")

# Thread para receber pedidos de subscrição
receive_thread = threading.Thread(target=receive_requests)
receive_thread.start()

def get_input():
    global interval
    while True:
        str = input()
        if str.startswith("setinterval"):
            interval = float(str.split(" ")[1])
            print("Interval set to " + str.split(" ")[1] + " seconds.")

# Thread para ler input do teclado
input_thread = threading.Thread(target=get_input)
input_thread.start()

# Mantém o programa rodando
send_thread.join()